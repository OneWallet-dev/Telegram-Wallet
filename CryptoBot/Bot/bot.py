from aiogram import Dispatcher
from aiogram.client.session import aiohttp
from aiogram.fsm.storage.redis import RedisStorage

from AllLogs.bot_logger import BotLogger
from Bot.handlers import start_hand
from Bot.handlers.service_functions import return_hand, AML_check_hand
from Bot.handlers.Transaction_metods import transfer_hand
from Bot.handlers.main_handlers import transaction_menu_hand, auth_hand, main_menu_hand, registration_hand, wallet_hand
from Bot.middleware.alive_middle import AliveMiddleware
from Bot.middleware.db import DbSession
from Dao.DB_Postgres.session import create_session
from Dao.DB_Redis import RedRedis
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

    dp.include_router(main_menu_hand.router)
    dp.include_router(return_hand.router)

    dp.include_router(wallet_hand.router)
    dp.include_router(transaction_menu_hand.router)
    dp.include_router(transfer_hand.router)

    dp.include_router(AML_check_hand.router)

    # wallets

    session = aiohttp.ClientSession()
    await session.close()

    await RedRedis.connect_to_storage()
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
