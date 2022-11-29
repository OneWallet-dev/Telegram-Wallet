from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from Dao.DB_Redis import DataRedis


class AliveMiddleware(BaseMiddleware):
    redis = DataRedis()

    async def __call__(self,
                       handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message | CallbackQuery,
                       data: Dict[str, Any]
                       ):
        user_id = event.from_user.id if isinstance(event, Message) else event.message.from_user.id
        was_alive = await self.redis.update_user_life(user_id)

        if not was_alive:
            state: FSMContext = data.get("state")
            await state.clear()

        return await handler(event, data)
