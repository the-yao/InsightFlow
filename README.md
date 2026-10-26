# InsightFlow · 数据分析智能体

对话式数据分析平台：上传 CSV 表格，用自然语言提问，AI 自动调用工具完成**汇总、异常检测、列统计**，并把每一步进度流式返回给前端。

## 项目亮点（面试重点）

- **LangGraph 状态机编排 Agent**：`StateGraph` + `MessagesState` + `ToolNode` + 条件边，支持多轮工具调用，每步可观测、可测试。
- **自定义工具**：把 pandas 分析函数用 `@tool` 封装成 LLM 可调用的工具（`query_data` / `detect_anomaly` / `summarize_column`）。
- **双模型一条协议切换**：DeepSeek / Ollama 都走 OpenAI 兼容接口，改一行配置即可切换，本地调试与正式分析零成本互换。
- **流式输出 + SSE**：`astream` 逐节点产出，SSE 实时推给前端，用户不用干等最终结果。

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python 3.13 · FastAPI · SQLAlchemy 2.0 · pydantic-settings · Uvicorn |
| Agent | LangGraph · LangChain（ChatOpenAI）· DeepSeek · Ollama |
| 数据 | pandas · SQLite（开发）/ PostgreSQL（生产）|
| 前端 | Next.js · React · TypeScript · Tailwind（开发中）|

## 项目结构

```
InsightFlow/
├── backend/
│   ├── app/
│   │   ├── agent/
│   │   │   ├── graph.py       # Agent 核心：LangGraph 状态机 + 流式执行
│   │   │   └── tools.py       # pandas 工具（@tool 封装）
│   │   ├── api/
│   │   │   ├── datasets.py    # CSV 上传 / 查询 / schema 推断
│   │   │   └── analysis.py    # SSE 流式分析接口
│   │   ├── core/              # 配置 / LLM / 数据库
│   │   ├── models/            # SQLAlchemy ORM 模型
│   │   └── main.py            # FastAPI 入口
│   ├── run_agent.py           # 终端交互入口
│   ├── requirements.txt
│   └── sales.csv              # 示例数据
├── docs/
│   ├── decisions.md           # 架构决策记录（含面试 Q&A）
│   └── ERROR_LOG.md           # 开发踩坑记录
├── docker-compose.yml         # Postgres + Redis（生产 / 定时任务）
└── frontend/                  # 前端（开发中）
```

## 快速开始

### 1. 环境准备

需要 Python 3.13，在 `backend` 目录创建并激活虚拟环境：

```bash
cd backend
python -m venv venv

# Windows 激活：
venv\Scripts\Activate.ps1
# macOS / Linux 激活：
source venv/bin/activate

pip install -r requirements.txt
```

### 2. 配置 .env

在 `backend` 目录新建 `.env` 文件，填入以下内容（密钥换成你自己的，文件不要提交 git）：

```env
DATABASE_URL=sqlite:///./insightflow.db
LLM_PROVIDER=deepseek        # deepseek | ollama
DEEPSEEK_API_KEY=sk-xxxx      # 你的 DeepSeek key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=qwen2.5:7b
```

### 3. 终端交互运行 Agent

```bash
cd backend
python run_agent.py
# 先选择模型 1.DeepSeek / 2.Ollama，再输入你的分析问题
```

### 4. 启动 API + Swagger 文档

```bash
cd backend
uvicorn app.main:app --reload
# 打开 http://localhost:8000/docs
```

### 5. 流式分析接口（SSE）

```
GET /analysis/stream?question=按月份汇总销售额，并检查异常
```

### 6. Docker 启动 Postgres + Redis

```bash
docker compose up -d
```

## 功能

- CSV 上传 + 列类型 / schema 自动推断（含样例值、缺失值统计）
- 自然语言数据分析：按维度汇总、异常检测、列统计
- SSE 流式进度推送（区分 agent / tools 节点）

## 架构决策与踩坑记录

- [docs/decisions.md](docs/decisions.md)：每个技术选型的「为什么 + 替代方案 + 面试追问预演」
- [docs/ERROR_LOG.md](docs/ERROR_LOG.md)：开发过程中踩过的坑与解决方案

## 下一步计划

- [ ] 前端分析页（SSE 流式渲染）
- [ ] 定时任务（Celery + Redis）
- [ ] 知识库 RAG 检索
- [ ] 单元测试（pytest）