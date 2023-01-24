import redis.asyncio as aioredis
from redis.asyncio.connection import ConnectionPool
from config import config


class Redis:
    main_base = 0
    data_redis: ConnectionPool

    @classmethod
    async def connect_to_storage(cls):

        cls.data_redis = await aioredis.from_url(
            f"{config.REDIS_URL}{cls.main_base}", decode_responses=True)


class DataRedis(Redis):

    @classmethod
    async def set_key(cls, key: str, value: str, ttl=-1):
        return await cls.data_redis.set(key, value, ex=ttl)


    @classmethod
    async def get_data(cls, key: str):
        return await cls.data_redis.get(key)
