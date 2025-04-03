"""
数据库连接 - 数据库连接和会话管理
"""
import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取数据库URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/autogen_db")

# 创建异步引擎
engine = create_async_engine(
    DATABASE_URL, 
    echo=False, 
    future=True,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=20
)

# 创建异步会话工厂
async_session_factory = async_sessionmaker(
    engine, 
    expire_on_commit=False, 
    autoflush=False, 
    autocommit=False,
    class_=AsyncSession
)

# 基础模型类
class Base(AsyncAttrs, DeclarativeBase):
    """基础模型类"""
    pass

# 使用上下文管理器模式获取数据库会话
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话"""
    session = async_session_factory()
    try:
        yield session
        # 添加自动提交逻辑
        await session.commit()
    except Exception as e:
        # 发生异常时回滚
        await session.rollback()
        raise
    finally:
        await session.close()

# 导出这些组件，以便其他模块可以从这里导入
__all__ = ['Base', 'engine', 'get_db', 'async_session_factory', 'AsyncSession']
