from aiogram import Bot, Dispatcher, Router

from config import config


async def start_bot():

    bot = Bot(config.BOT_TOKEN, parse_mode="HTML")

    bot_info = await bot.get_me()

    print(f"Bot was reborn as\n"
          f"|- {bot_info.full_name} -|- @{bot_info.username} -|\n"
          f"What a time to be alive!\n")

    dp = Dispatcher()


    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
