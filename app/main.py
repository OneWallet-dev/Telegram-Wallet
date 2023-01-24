import asyncio

from api.database import postgres, redis
from api.tests import test_user
from bot.bot import start_bot


async def main():
    await postgres.Postgres().connect_to_storage()
    await redis.Redis().connect_to_storage()
    await start_bot()




if __name__ == '__main__':
    asyncio.run(main())


