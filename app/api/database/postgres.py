from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config import config
Base = declarative_base()


class Postgres:
    async_session: sessionmaker

    @classmethod
    async def connect_to_storage(cls):
        engine_pg = create_async_engine(config.POSTGRES_URL, echo=False)

        cls.async_session = sessionmaker(engine_pg, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    """
    Dependency function that yields db sessions
    """
    async with Postgres().async_session() as session:
        yield session
        await session.commit()

