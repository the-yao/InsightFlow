# InsightFlow 错误日志

> 规则：每次遇到报错或排查问题时，按模板追加一条记录。定期回顾，避免重复踩坑。
> 编号规则：ERR-001 递增；状态：未解决 / 已解决 / 已预防。

---

## ERR-001 SQLAlchemy 导入名拼写错误导致无法运行

- **日期**：2026-09-14
- **阶段**：阶段 0（工程化脚手架）
- **报错信息**：`ImportError: cannot import name 'Txet' from 'sqlalchemy'`（同类：`ForeigenKey`）
- **原因分析**：[models/__init__.py](backend/app/models/__init__.py) 中手写导入时拼错单词：`Txet` → `Text`，`ForeigenKey` → `ForeignKey`。IDE 没有自动补全，纯手打容易错。
- **解决方案**：修正为 `from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, JSON`。
- **教训/知识点**：导入报错 `cannot import name 'X'`，99% 是拼写错误或该模块里根本没有这个名字。写导入语句时用 IDE 自动补全，不要手打。
- **状态**：已解决

---

## ERR-002 分层职责错误：create_engine 放进了 models

- **日期**：2026-09-14
- **阶段**：阶段 0（工程化脚手架）
- **报错信息**：（无运行时报错，属于架构问题，代码能跑但结构不对）
- **原因分析**：`models/__init__.py` 开头写了 `from sqlalchemy import create_engine`。models 的职责是"定义表结构"，"连接数据库"（create_engine/SessionLocal）属于 core/database.py 的职责。
- **解决方案**：`create_engine` 移入 `app/core/database.py`，models 只保留表定义。
- **教训/知识点**：分层目录的意义——api 管路由、core 管基础设施、models 管表定义。一个文件只做一类事，报错时才能快速定位。
- **状态**：已解决

---

## ERR-003 pydantic-settings 不在 requirements.txt 中

- **日期**：2026-09-14
- **阶段**：阶段 0（工程化脚手架）
- **报错信息**：（预期会报）`ModuleNotFoundError: No module named 'pydantic_settings'`
- **原因分析**：`app/core/config.py` 用了 `pydantic_settings.BaseSettings`，但原 requirements.txt 没有这个包（它和 pydantic 是两个包）。
- **解决方案**：`pip install pydantic-settings`，并补进 requirements.txt。
- **教训/知识点**：`pydantic` 和 `pydantic-settings` 是两个独立的包。新增第三方库后要同步更新 requirements.txt，否则换机器/部署时必炸。
- **状态**：已预防

---

## ERR-004 FastAPI 文件上传缺 python-multipart

- **日期**：2026-09-14
- **阶段**：阶段 1（数据接入层）
- **报错信息**：（预期会报）`Form data requires "python-multipart" to be installed.`
- **原因分析**：`UploadFile`/`File` 走的是 multipart/form-data 编码，解析需要 python-multipart 包，FastAPI 不会自动装。
- **解决方案**：`pip install python-multipart`，并补进 requirements.txt。
- **教训/知识点**：这是 FastAPI 新手第一大坑。凡是用到表单/文件上传，先装 python-multipart。
- **状态**：已预防

---

<!-- 新记录请追加在此行下方，保持编号递增 -->

## ERR-004 启动目录错误：根目录下运行 uvicorn 找不到 app 模块

- **日期**：2026-09-17
- **阶段**：阶段 1（数据接入层）
- **报错信息**：`ModuleNotFoundError: No module named 'app'`
- **原因分析**：在项目根目录 `E:\aiproject\InsightFlow` 下执行 `uvicorn app.main:app --reload`，但 `app` 包位于 `backend\app\`，uvicorn 从当前目录（根目录）查找 `app` 模块，根目录下不存在，故报找不到模块。
- **解决方案**：先 `cd` 到 `backend` 目录，再启动：`cd e:\aiproject\InsightFlow\backend` 后 `uvicorn app.main:app --reload`。
- **教训/知识点**：uvicorn 的 `app.main:app` 中的 `app` 是相对于**当前工作目录**的模块路径。启动前先确认命令提示符所在的目录是否包含 `app` 包。判定标准：提示符应显示 `...\backend>`，而非项目根目录。
- **状态**：已解决

---

## ERR-005 路由装饰器误用 f-string 与 response_model 类型错误

- **日期**：2026-09-17
- **阶段**：阶段 1（数据接入层）
- **报错信息**：`NameError: name 'dataset_id' is not defined`
- **原因分析**：详情接口装饰器写成 `@router.get(f"/{dataset_id}", response_model=list[DatasetOut])`，有两处错误：① 路径用了 f-string，Python 会在导入时立刻求值 `{dataset_id}`，但此时变量尚未定义，故抛 NameError；② `response_model` 误写为 `list[DatasetOut]`，详情接口返回的是单条数据而非列表。
- **解决方案**：路径改用普通字符串 `"/{dataset_id}"`，`response_model` 改为 `DatasetOut`。FastAPI 的 `{dataset_id}` 是路径占位符，由框架请求时注入，不应提前求值。
- **教训/知识点**：① FastAPI 路径里的 `{参数}` 是占位符，用普通字符串写，不要用 f-string；② `response_model` 要匹配实际返回结构——列表接口用 `list[X]`，详情接口用 `X`。
- **状态**：已解决

---

## ERR-006 上传接口 500：user_id 非空约束与暂不传值冲突

- **日期**：2026-09-17
- **阶段**：阶段 1（数据接入层）
- **报错信息**：Swagger Server response 空白（实际为 500）；uvicorn 终端出现 `sqlalchemy.exc.IntegrityError: NOT NULL constraint failed: datasets.user_id`
- **原因分析**：`Dataset.user_id` 定义为 `Mapped[int]`（非空），但上传接口按计划暂不传 user_id（阶段 4 才加认证），`db.commit()` 时违反非空约束，未捕获异常导致 500。
- **解决方案**：models 中改为 `user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)`；因 SQLite 已按旧结构建表，需删除 `insightflow.db` 重新执行 `init_db()`。
- **教训/知识点**：① 表结构（models）与业务代码（api）必须一致——列是否可空在设计时就应确定；② 改表结构后 SQLite 不会自动生效，必须删库重建（开发期）或用迁移工具（Alembic，后期）；③ Swagger 空白/500 时，第一现场在 uvicorn 终端的 traceback，先看终端再猜。
- **状态**：已解决
