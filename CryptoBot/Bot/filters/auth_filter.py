from aiogram.filters import Filter
from aiogram.types import User, Message, CallbackQuery

from Dao.DB_Redis import RedRedis, DataRedis


class NotAuthFilter(Filter):

    async def __call__(self, event: Message | CallbackQuery) -> bool:
        user_id = event.from_user.id
        is_auth_value = await DataRedis.get_data(f"Users: {user_id}: authorized")
        if not is_auth_value or is_auth_value == 'False':
            return True
        elif is_auth_value == "True":
            return False
        else:
            raise Exception("Bad auth state in redis data database!")
