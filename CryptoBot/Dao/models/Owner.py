import datetime
from contextlib import suppress
from string import ascii_letters, digits

from Crypto.Random import random
from aiogram.types import User
from cryptography.hazmat.primitives import hashes
from sqlalchemy import Column, String, DateTime, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection

from Bot.exeptions.wallet_ex import DuplicateToken
from Bot.utilts.currency_helper import base_tokens
from Dao.DB_Postgres.session import create_session, Base
from Dao.models.Address import Address
from Dao.models.Token import Token
from Dao.models.Wallet import Wallet


class Owner(Base):
    __tablename__ = "owners"

    id = Column(String, primary_key=True, unique=True)
    datetime_come = Column(DateTime, default=datetime.datetime.now())
    password = Column(String, default=None)
    wallets: dict[str, Wallet] = relationship(
        "Wallet",
        collection_class=attribute_mapped_collection("blockchain"),
        cascade="all, delete-orphan", lazy="joined"
    )

    @staticmethod
    async def _form_uid():
        session_connect = await create_session()
        async with session_connect() as session:
            reform = True
            while reform:
                string = ascii_letters + digits
                result = ''.join((random.choice(string) for _ in range(7))).upper()
                reform = True if await session.get(Owner, result) else False
        return result

    @staticmethod
    async def register(password: str | None = None):
        """ For new users """
        session_connect = await create_session()
        async with session_connect() as session:
            password = Owner._password_encode(password)
            uid = await Owner._form_uid()
            try:
                stmt = insert(Owner).values(id=uid, password=password)
                do_nothing = stmt.on_conflict_do_nothing(index_elements=['id'])
                await session.execute(do_nothing)
                await session.commit()
                return uid
            except IntegrityError:
                await session.rollback()
                raise

    @staticmethod
    async def password_check(session: AsyncSession, uid: str, password: str):
        owner: Owner = await session.get(Owner, uid)
        phash = Owner._password_encode(password)
        return True if owner.password == phash else False

    @staticmethod
    def _password_encode(text: str):
        digest = hashes.Hash(hashes.SHA256())
        digest.update(bytes(text, "UTF-8"))
        result = digest.finalize()
        return str(result)
