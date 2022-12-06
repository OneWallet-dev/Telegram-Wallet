from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery

from Dao.DB_Redis import DataRedis


class NotAuthFilter(Filter):

    async def __call__(self, event: Message | CallbackQuery) -> bool:
        user_id = event.from_user.id
        is_auth_value = await DataRedis.get_data(f"Users: {user_id}: authorized")
        if not is_auth_value or is_auth_value == 'False':
            return True
        else:
            return False


class AuthTimeout(Filter):

    async def __call__(self, event: Message | CallbackQuery) -> bool:
        user_id = event.from_user.id
        tries = await DataRedis.auth_cooldown(user_id)
        if tries >= 5:
            return True
        else:
            return False
