from aiogram import Dispatcher
from aiogram.client.session import aiohttp
from aiogram.fsm.storage.redis import RedisStorage

from AllLogs.bot_logger import BotLogger
from Bot.handlers import start_hand, wallet_hand, return_hand, AML_check, m_menu_hand, registration_hand, auth_hand
from Bot.middleware.alive_middle import AliveMiddleware
from Bot.middleware.db import DbSession
from Databases.DB_Postgres.session import create_session
from Databases.DB_Redis import RedRedis
from bata import Data

storage = RedisStorage.from_url(RedRedis.states_base_url())
dp = Dispatcher(storage=storage)

async def bot_start():
    BotLogger()

    bot = Data.main_bot
    bot_info = await bot.get_me()

    print(f"Bot was reborn as\n"
          f"|- {bot_info.full_name} -|- @{bot_info.username} -|\n"
          f"What a time to be alive!\n")

    session_db = await create_session()
    dp.message.middleware(DbSession(session_db))
    dp.callback_query.middleware(DbSession(session_db))
    dp.message.middleware(AliveMiddleware())

    dp.include_router(start_hand.router)
    dp.include_router(registration_hand.router)
    dp.include_router(auth_hand.router)

    dp.include_router(m_menu_hand.router)

    dp.include_router(return_hand.router)
    dp.include_router(wallet_hand.router)
    dp.include_router(AML_check.router)

    # wallets

    session = aiohttp.ClientSession()
    await session.close()

    await RedRedis.connect_to_storage()
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
