import logging
import os

import cryptoapis
from aiogram import Dispatcher
from aiogram.client.session import aiohttp
from aiogram.fsm.storage.redis import RedisStorage
from cryptoapis.api import assets_api

from AllLogs.bot_logger import BotLogger
from Bot.handlers import start_hand, wallet_hand, return_hand
from Bot.middleware.db import DbSession
from Bot.utilts.cleaner import Cleaner
from Databases.DB_Postgres.session import create_session
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

    session_db = await create_session()
    dp.message.middleware(DbSession(session_db))
    dp.callback_query.middleware(DbSession(session_db))

    dp.include_router(start_hand.router)
    dp.include_router(return_hand.router)
    dp.include_router(wallet_hand.router)

    #wallets

    session = aiohttp.ClientSession()
    await session.close()

    await RedRedis.connect_to_storage()
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
