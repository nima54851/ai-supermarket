import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

SQLITE_DB_PATH = os.getenv("DATABASE_URL", "sqlite:///./ad_platform.db")

# SQLite配置
engine = create_engine(
    SQLITE_DB_PATH,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """初始化数据库"""
    import models
    Base.metadata.create_all(bind=engine)