import logging

from aiogram import Dispatcher
from aiogram.client.session import aiohttp
from aiogram.fsm.storage.redis import RedisStorage

from AllLogs.bot_logger import BotLogger
from Bot.handlers import start_hand
from Databases.DB_Postgres import create_session
from Databases.DB_Redis import RedRedis
from bata import Data

BotLogger()
storage = RedisStorage.from_url(RedRedis.states_base_url())
dp = Dispatcher(storage=storage)


async def bot_start():
    bot = Data.main_bot
    bot_info = await bot.get_me()
    print(f"Bot was reborn as\n"
          f"|- {bot_info.full_name} -|- @{bot_info.username} -|\n"
          f"What a time to be alive!\n")

    dp.include_router(start_hand.router)

    session = aiohttp.ClientSession()
    await session.close()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
