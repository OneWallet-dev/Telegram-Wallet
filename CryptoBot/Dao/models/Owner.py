import datetime

from aiogram.types import User
from cryptography.hazmat.primitives import hashes
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection

from Bot.utilts.currency_helper import base_tokens
from Dao.models.models import Base
from Dao.models.Token import Token
from Dao.models.Wallet import Wallet


class Owner(Base):
    __tablename__ = "owners"

    id = Column(String, primary_key=True, unique=True)
    username = Column(String)
    datetime_come = Column(DateTime, default=datetime.datetime.now())
    password = Column(String, default=None)
    wallets: dict[str: Wallet] = relationship(
        "Wallet",
        collection_class=attribute_mapped_collection("blockchain"),
        cascade="all, delete-orphan", lazy="joined"
    )

    async def createWallet(self, session: AsyncSession, blockchain: str):
        pass

    @staticmethod
    async def register(session: AsyncSession, user: User, password: str | None = None):
        """ For new users """
        password = Owner._password_encode(password)
        try:
            stmt = insert(Owner).values(id=str(user.id), username=user.username, password=password)
            do_nothing = stmt.on_conflict_do_nothing(index_elements=['id'])
            await session.execute(do_nothing)
            await session.commit()
            return await session.get(Owner, str(user.id))
        except IntegrityError:
            await session.rollback()
            raise

    @staticmethod
    async def password_check(session: AsyncSession, user: User, text: str):
        owner: Owner = await session.get(Owner, str(user.id))
        phash = Owner._password_encode(text)
        return True if owner.password == phash else False

    @staticmethod
    def _password_encode(text: str):
        digest = hashes.Hash(hashes.SHA256())
        digest.update(bytes(text, "UTF-8"))
        result = digest.finalize()
        return str(result)

    @staticmethod
    async def add_currency(session: AsyncSession, user: User, token: str, network: str):
        owner: Owner = await session.get(Owner, str(user.id))
        wallets: dict[str, Wallet] = owner.wallets
        wall = wallets[network]
        wall.tokens.append(Token(token_name=token, contract_Id=base_tokens[token]['contract_address']))
        session.add(wall)
        await session.commit()
