from aiogram.filters import Filter
from aiogram.types import CallbackQuery

from Dao.models.Owner import Owner
from Dao.DB_Postgres.session import create_session
from Dao.DB_Redis import RedRedis


class ChainOwned(Filter):
    def __init__(self):
        self.redis = RedRedis()

    async def __call__(self, callback: CallbackQuery) -> bool:
        chain = callback.data
        user_id = callback.from_user.id
        user_have_it = await self.redis.user_currency_cache_check(user_id, chain)
        if not user_have_it:
            ses = await create_session()
            async with ses() as session:
                owner: Owner = await Owner.get(session, user=callback.from_user)
                result = set(owner.wallets)
                await self.redis.user_currency_cache_update(user_id=user_id, currencies=result)
                if chain not in result:
                    return False
        else:
            return True
