import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy.orm import selectinload
from bata import Data

data = Data()
Base = declarative_base()
bot = data.main_bot


async def create_session():
    engine = create_async_engine(
        f'postgresql+asyncpg://{data.postgres_user}:{data.postgres_password}@{data.postgres_host}/postgres'
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async_sessionmaker = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    async_sessionmaker()
    return async_sessionmaker
