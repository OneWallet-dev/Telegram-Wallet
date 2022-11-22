from aiogram.filters import Filter
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from Databases.DB_Postgres.models import Owner
from Databases.DB_Redis import RedRedis


class ChainOwned(Filter):
    def __init__(self):
        self.redis = RedRedis()

    async def __call__(self, message: Message, session: AsyncSession) -> bool:
        currency_name = message.text
        # chain = chain_finder(currency_name)
        user_id = message.from_user.id
        user_have_it = await self.redis.user_currency_cache_check(user_id, currency_name)
        if not user_have_it:
            owner: Owner = await Owner.get(session, user=message.from_user)

            result = set()
            await self.redis.user_currency_cache_update(user_id=user_id, currencies=result)
            if currency_name not in result:
                return False
        else:
            return True
