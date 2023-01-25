from typing import Callable, Dict, Awaitable, Any

from aiogram import Bot, Dispatcher, Router, BaseMiddleware
from aiogram.types import TelegramObject

from api.database.postgres import Postgres
from bot import router_stast

from config import config

class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_pool):
        super().__init__()
        self.session_pool = session_pool

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        async with self.session_pool() as session:
            data["session"] = session
            return await handler(event, data)

async def start_bot():

    bot = Bot(config.BOT_TOKEN, parse_mode="HTML")


    bot_info = await bot.get_me()

    print(f"Bot was reborn as\n"
          f"|- {bot_info.full_name} -|- @{bot_info.username} -|\n"
          f"What a time to be alive!\n")

    dp = Dispatcher()
    dp.message.middleware(DbSessionMiddleware(Postgres().async_session))

    dp.include_router(router_stast.router)


    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
