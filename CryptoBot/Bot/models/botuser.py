from contextlib import suppress

from aiogram.types import User
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from Databases.DB_Postgres.models import Users


class BotUser:
    wallets: dict[str:]

    def __init__(self, session: AsyncSession, user: User):
        self.session: AsyncSession = session
        self.telegram_id: int | str = user.id
        self.username: str = user.username

    async def create(self, password: str | None = None):
        print(self.telegram_id, self.username)
        stmt = insert(Users).values(user_id=self.telegram_id,
                                    username=self.username,
                                    )
        do_nothing = stmt.on_conflict_do_nothing(index_elements=['user_id'])
        # TODO: Why execute and commint?
        await self.session.execute(do_nothing)
        with suppress(IntegrityError):
            await self.session.commit()

    async def get_user(self):
        pass

    async def create_wallet(self):
        pass
