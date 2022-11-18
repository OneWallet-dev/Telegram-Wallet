from aioredis import from_url

from bata import Data


class RedRedis:
    password = Data.redis_password
    host = Data.redis_host
    port = Data.redis_port
    bot_states_base = 0
    bot_storage_base = 1

    @classmethod
    def states_base_url(cls):
        return f"redis://:{cls.password}@{cls.host}:{cls.port}/{cls.bot_states_base}"

    @classmethod
    async def bot_storage_conn(cls, db_number):
        return from_url(f"redis://:{cls.password}@{cls.host}:{cls.port}/{cls.bot_storage_base}")

