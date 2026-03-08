from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from sqlalchemy import create_engine

async_engine = create_async_engine(settings.DB_URL_ASYNC, echo=True)
sync_engine = create_engine(settings.DB_URL_SYNC, echo=True)

AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

SessionLocal = sessionmaker(
    bind=sync_engine,
    autoflush=False,
    autocommit=False
)

async def get_db() -> AsyncSessionLocal:
    async with AsyncSessionLocal() as session:
        yield session

async def close_db_engine() -> None:
    await async_engine.dispose()
