from typing import Optional

from aiogram import Bot
from aiogram.client.session.base import BaseSession

from Databases.DB_Postgres import create_session


class heir_Bot(Bot):
    def __init__(self,
                 token: str,
                 session: Optional[BaseSession] = None,
                 parse_mode: Optional[str] = None,
                 ):
        Bot.__init__(self, token, parse_mode=parse_mode, session=session)

    @staticmethod
    async def get_db_session():
        session = await create_session()
        return session
