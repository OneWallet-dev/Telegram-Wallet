import logging
from aiogram import Dispatcher
from aiogram.client.session import aiohttp
from aiogram.fsm.storage.redis import RedisStorage
from AllLogs.bot_logger import BotLogger
from Bot.handlers import start_hand, wallet_hand
from Bot.handlers.wallets import TRON
from Bot.middleware.db import DbSession
from Bot.wallet_generator.wallet_generator import wallet_bip44
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

    session_db = await create_session()
    dp.message.middleware(DbSession(session_db))
    dp.callback_query.middleware(DbSession(session_db))

    dp.include_router(start_hand.router)
    dp.include_router(wallet_hand.router)

    #wallets
    dp.include_router(TRON.router)

    session = aiohttp.ClientSession()
    await session.close()

    await RedRedis.connect_to_storage()
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
