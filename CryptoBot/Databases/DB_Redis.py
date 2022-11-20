import redis.asyncio as aioredis
from redis.asyncio.connection import ConnectionPool

from bata import Data


class RedRedis:
    password = Data.redis_password
    host = Data.redis_host
    port = Data.redis_port
    cache_time = 86400
    bot_states_base = 0
    bot_storage_base = 1
    user_currency_cache_key = "Users:{user:n}:currency_set"
    data_redis: ConnectionPool

    @classmethod
    def states_base_url(cls):
        return f"redis://:{cls.password}@{cls.host}:{cls.port}/{cls.bot_states_base}"

    @classmethod
    async def connect_to_storage(cls):
        cls.data_redis = await aioredis.from_url(
            f"redis://:{cls.password}@{cls.host}:{cls.port}/{cls.bot_storage_base}", decode_responses=True)

    async def user_currency_cache_check(self, user_id: int, currency: str):
        return await self.data_redis.sismember(self.user_currency_cache_key.format(user=user_id), currency)

    async def user_currency_cache_update(self, user_id: int, currencies: set[str]):
        for currency in currencies:
            await self.data_redis.sadd(self.user_currency_cache_key.format(user=user_id), currency)
        await self.data_redis.expire(self.user_currency_cache_key.format(user=user_id), self.cache_time)
