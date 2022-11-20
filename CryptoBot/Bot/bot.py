import logging
import os
from aiogram import Dispatcher
from aiogram.client.session import aiohttp
from aiogram.fsm.storage.redis import RedisStorage

from AllLogs.bot_logger import BotLogger
from Bot.handlers import start_hand, wallet_hand
from Bot.middleware.db import DbSession
from Bot.mnemonic_generator.mnemonic import Mnemonic
from Databases.DB_Postgres import create_session
from Databases.DB_Redis import RedRedis
from bata import Data
from bip_utils import *

BotLogger()
storage = RedisStorage.from_url(RedRedis.states_base_url())
dp = Dispatcher(storage=storage)

#m/44'/195'/0'/0/0
async def bot_start():
    bot = Data.main_bot
    bot_info = await bot.get_me()
    ADDR_NUM: int = 5
    mnemo = Mnemonic()
    words = mnemo.generate_mnemo(strength=256)
    print("MNEMONIC", words)

    seed_bytes = Bip39SeedGenerator(words).Generate()

    bip44_mst_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.TRON)

    # root key совпадает
    print(f"BIP32 Root Key: {bip44_mst_ctx.PrivateKey().ToExtended()}")

    #PublicKey = bip44_mst_ctx.PrivateKey().PublicKey()

    #addr = TrxAddr.EncodeKey()
    #print(addr)


    print(f"Bot was reborn as\n"
          f"|- {bot_info.full_name} -|- @{bot_info.username} -|\n"
          f"What a time to be alive!\n")

    session = await create_session()
    dp.message.middleware(DbSession(session))
    dp.callback_query.middleware(DbSession(session))

    dp.include_router(start_hand.router)
    dp.include_router(wallet_hand.router)

    session = aiohttp.ClientSession()
    await session.close()

    await RedRedis.connect_to_storage()
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
