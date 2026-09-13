"""HALLMARK Database Configuration — Async SQLAlchemy + PostgreSQL."""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://localhost:5432/hallmark")
DATABASE_URL_SYNC = os.getenv("DATABASE_URL_SYNC", "postgresql://localhost:5432/hallmark")

engine = create_async_engine(DATABASE_URL, echo=False, pool_size=5, max_overflow=10)
sync_engine = create_engine(DATABASE_URL_SYNC, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_session():
    async with async_session() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
