# 架构决策记录（ADR）

> 目的：沉淀每个关键技术选型的「选型 + 为什么 + 替代方案 + 面试追问预演」。这是你面试前的弹药库，面试前逐条过一遍。
> 用法：每完成一个模块补一条；只记「会影响后续走向」的决策，不记琐碎细节。

## 记录模板（新增决策时复制）

### ADR-编号：一句话标题
- **选型**：用了什么技术/方案
- **为什么**：选它的核心理由（1-3 句）
- **替代方案**：还能用什么？各自的优劣
- **面试追问预演**：面试官可能怎么问，我怎么答（自己填）

---

## ADR-001 后端框架选 FastAPI

- **选型**：FastAPI（asyncio 异步框架）
- **为什么**：自动生成 Swagger 交互文档、原生 async、用 Pydantic 做数据校验、类型提示友好；它是 Python 做 LLM 应用的事实标准，和 LangChain 生态无缝衔接。
- **替代方案**：Flask（简单但无原生 async、无自动文档、校验要手动）；Django（全家桶但重，其 ORM/Admin 在本项目用不上）。本条领域内 FastAPI 是主流选择。
- **面试追问预演**：（待补）FastAPI 的 async 和 Flask 多线程模型的区别？`def` 和 `async def` 路由的差异？

## ADR-002 数据库：SQLite 起步、Postgres 作为生产

- **选型**：开发期 SQLite，生产/联调切 Postgres（`database_url` 一改即换）。
- **为什么**：SQLite 零配置、单文件、让阶段 0/1 快速跑通；通过 ORM（SQLAlchemy）隔离，切换只改连接串，不影响业务代码。
- **替代方案**：全程 SQLite（并发弱、无服务端、生产不可用）；起步就用 Postgres（需 Docker 依赖，学习期起步慢）。故「起步 SQLite + 抽象好切 Postgres」性价比最高。
- **面试追问预演**：（待补）SQLite 和 Postgres 的核心区别？为什么生产不用 SQLite？

## ADR-003 ORM 用 SQLAlchemy 2.0 风格（Mapped / mapped_column）

- **选型**：SQLAlchemy 2.0 的 `Mapped[...]` + `mapped_column` 声明式写法。
- **为什么**：类型提示完整（IDE 能补全、能静态检查）、表关系用 `relationship` 表达更清晰、生态最成熟。
- **替代方案**：直接写 SQL 字符串（灵活但易注入、无类型安全）；Django ORM（绑定 Django 框架，不适配本项目）；peewee（轻量但生态弱）。SQLAlchemy 是 Python 后端主流。
- **面试追问预演**：（待补）`relationship` 的左右两侧各代表什么？`ForeignKey("users.id")` 的字符串为什么能引用未定义的类？

## ADR-004 配置/密钥管理用 pydantic-settings + .env

- **选型**：`pydantic-settings.BaseSettings` 读 `.env`，`.env` 进 `.gitignore`。
- **为什么**：配置与代码分离；密钥不泄露进 git；字段带类型 + 默认值，读错配置启动时即报错而非运行时。
- **替代方案**：硬编码在代码里（密钥泄漏、改环境要改代码）；手动 `os.getenv`（无默认值、无类型、易拼错）。
- **面试追问预演**：（待补）为什么 `.env` 不能提交 git？多环境（dev/prod）配置怎么做？

## ADR-005 LLM：用 OpenAI 兼容协议统一 DeepSeek / Ollama

- **选型**：`langchain_openai.ChatOpenAI` 通过改 `base_url` + `model` 在 DeepSeek 云端 API 和 Ollama 本地模型之间切换（见 `core/llm.py`）。
- **为什么**：DeepSeek 和 Ollama 都实现了 OpenAI 兼容接口，用同一个客户端即可，切换零成本——省成本时用本地 Ollama 调试，正式分析用 DeepSeek。
- **替代方案**：各家 SDK 分别封装（重复代码、切换成本高）；硬绑单一供应商（失去灵活性）。
- **面试追问预演**：（待补）OpenAI 兼容协议指的是什么？为什么很多大模型服务都声称自己是"OpenAI 兼容"？

---

## 待补充（按开发进度填）

### ADR-006 Agent 编排选 LangGraph（阶段 2.4 完成）

- **选型**：LangGraph 状态机 —— `StateGraph` + `MessagesState` + `ToolNode` + `add_conditional_edges`。
- **为什么**（手写 while 循环做不到的 3 点）：
  1. **可观测/可测试**：每个节点是独立单元，可单测、打日志、追踪每一步入参出参。
  2. **断点恢复**：checkpointer 持久化中间状态，中断后可续跑（省 token 省时间）。
  3. **流式输出**：`astream` 天然支持，配合 SSE 做实时进度推送。
- **替代方案**：裸 `while` 循环（能跑，但循环逻辑藏在一个 for 里，三件事都要自己造轮子）。
- **面试追问预演**：
  - *Node / State / Conditional Edge 是什么？* → State 是贯穿流程的数据（这里是 messages 列表）；Node 是接收 State 返回增量的函数；Conditional Edge 根据 State 决定下一步去哪。
  - *状态机如何决定终止？* → `should_continue` 看最后一条 AIMessage 的 `tool_calls` 是否为空。补充更稳的方案：最大迭代次数上限、显式 stop 标志、`finish_reason`。
  - *MessagesState 的 reducer 作用？* → `add_messages` 让节点返回的 messages **追加而非覆盖**，否则模型每轮只能看到最后一条，等于失忆。

### ADR-007 工具函数返回值必须可 JSON 序列化（已踩坑）

- **选型**：工具返回值在绑给 LLM 前，统一转成原生 Python 类型（`float()`/`int()`/`str()`）。
- **为什么**：pandas 返回 `np.float64` / `np.int64`，`json.dumps` 会炸，且序列化进工具结果后模型可能读不懂。
- **替代方案**：`to_dict()` 后不转（炸）；自定义 JSON encoder（复杂，不必要）。
- **面试追问预演**：*pandas 的 numpy 类型和原生类型有什么区别？* → numpy 标量不是 Python 原生类型，无法被标准 json 序列化。

### ADR-008 Agent 错误处理与可观测性（阶段 2.6 加固后写）
LLM 返回畸形 tool_calls 怎么办、如何追踪每一步决策。

---

## 面试复盘 Q&A（阶段 2.4 前，标准答案要点）

> 面试官逐条问，自己先复述再看答案。错得最狠的是概念题，背到脱口而出。

### 基础概念（答错 = 硬伤）

- **invoke vs astream**：`invoke` 同步返回完整结果，适合批处理；`astream` 异步流式，每完成一个节点 yield 一段增量，配合 `stream_mode="updates"`，适合实时进度。本质是"拿最终态" vs "观察过程态"。

- **`provider = provider or settings.llm_provider`**：Python 短路求值，`or` 返回第一个真值。调用方传了 `provider` 用它，没传（None）回落 `.env` 默认值。删掉后 `provider=None`，`if provider == "ollama"` 恒 False，Ollama 切换失效。

- **`from langgraph.graph import StateGraph, MessagesState, START, END` 各项**：
  - `StateGraph`：图构造器（add_node / add_edge / compile）。
  - `MessagesState`：状态 schema（不是节点），`messages` 字段带 `add_messages` reducer。
  - `START`：入口虚拟节点；`END`：出口虚拟节点。

- **`tool_call_id` 干嘛的**：模型并行调多个工具时，让每个返回结果"对应回哪一次调用"，否则多结果一起回来会张冠李戴。手写循环时 `ToolMessage(tool_call_id=tc["id"])` 依次对号入座。

### 项目理解（看真懂还是背）

- **为什么 LangGraph 而非 while**：见 ADR-006 三理由。

- **MessagesState 为什么用 reducer**：`add_messages` 定义"新旧状态如何合并"——追加而非覆盖，保住对话历史，模型不失忆。

- **条件边靠什么信号终止**：`last.tool_calls` 是否为空。其他信号：最大迭代上限、显式 stop 标志、`finish_reason`。

- **2.3→2.4 为何"按产品"变"按月份"**：加了 SYSTEM_PROMPT，第 2 条"严格按用户指定维度，不要自作主张换维度"。4 条分别治：英文→中文、跑偏→忠实维度、反问→主动完成、编造→只用真实数据。

### 实战追问（最有区分度）

- **幻觉出不存在的工具名**：`TOOL_MAP[name]` 抛 KeyError 崩溃。兜底：try/except 捕获，返回 ToolMessage"工具 X 不存在，请重选"，让模型自我纠错，而非崩掉。

- **如何测试不确定输出的系统**：分层。工具函数是确定性的，用 pytest 正常单测；Agent 层不测"唯一答案"，只断言结构约束——调用了正确工具、参数符合 schema、输出引用了真实数据、遵守 system prompt。

- **任务完整性（漏做子任务）**：改 System Prompt（成本低但靠"祈求"）；Plan-and-Execute（先列步骤再逐条打勾，可靠但多一次 LLM 调用）。经典权衡"灵活不可靠 vs 可靠有开销"。

- **实时进度方案**：后端 `astream` 逐节点拿增量，SSE 单向推给前端（EventSource 接收）。选 SSE 而非 WebSocket：单向推送无需客户端回传，更简单省资源。