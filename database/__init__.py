from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from config import settings
from models.database import Base

async_session = sessionmaker(settings.engine, class_=AsyncSession, expire_on_commit=False)  # Пусть последнее останется


# Для FastApi Dependent
async def get_session_fastapi() -> AsyncSession:
    async with async_session(bind=settings.engine) as session:
        yield session


# Для запросов к БД
@asynccontextmanager
async def get_session():
    try:
        async with async_session() as session:
            yield session
    except:
        await session.rollback()
        raise
    finally:
        await session.close()


async def db_init():
    async with settings.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# async def insert_schedule(group_id, schedule, is_forced=True):
#     async with get_session() as session: