# 本文件负责“连接数据库”，与 models 的“定义表”职责分离
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings
from app.models import Base  # 导入它会触发 models/__init__.py 里所有表被注册

engine = create_engine(settings.database_url,echo=True) # echo=True 开发期打印 SQL，便于学习
SessionLocal = sessionmaker(bind=engine,autoflush=False,autocommit=False)

def get_db():
    #FastAPI 依赖注入用：每请求一个会话，用完关闭
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    #建表：把models里定义的所有表在数据库里创建出来
    Base.metadata.create_all(bind=engine)