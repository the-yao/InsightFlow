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

### ADR-006 Agent 编排选 LangGraph（阶段 2.4 完成后必写）
这是面试最高频的一条，务必说清：State 设计、conditional edge、为什么不用裸 while 循环、如何流式输出。

### ADR-007 工具函数返回值必须可 JSON 序列化（已踩坑）
`np.float64` / `np.int64` 无法被 `json.dumps`，绑给 LLM 前必须 `float()`/`int()` 转原生类型。

### ADR-008 Agent 错误处理与可观测性（阶段 2.6 加固后写）
LLM 返回畸形 tool_calls 怎么办、如何追踪每一步决策。