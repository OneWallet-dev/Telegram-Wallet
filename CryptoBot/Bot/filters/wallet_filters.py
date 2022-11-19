from aiogram.filters import Filter
from aiogram.types import Message

from Databases.DB_Redis import RedRedis


class WalletExists(Filter):
    def __init__(self):
        self.redis = RedRedis()

    async def __call__(self, message: Message) -> bool:
        currency_name = message.text
        # chain = chain_finder(currency_name)
        user_id = message.from_user.id
        user_have_it = await self.redis.user_currency_cache_check(user_id, currency_name)
        if not user_have_it:
            """
            Here getting list of all chains for user with given id. --> result
            """
            result = set()
            await self.redis.user_currency_cache_update(user_id=user_id, currencies=result)
            if currency_name not in result:
                return False
        else:
            return True
