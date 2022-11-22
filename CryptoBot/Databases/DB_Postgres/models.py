import datetime
from typing import Any

from aiogram.types import User
from sqlalchemy import Column, BigInteger, String, Float, DateTime, ForeignKey, Integer, Table, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base, relationship, context
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine, EncryptedType, StringEncryptedType

import Bot
import Databases
from bata import Data

Base = declarative_base()


class Transactions(Base):
    __tablename__ = "receipts"

    ID = Column(BigInteger, primary_key=True, unique=True, autoincrement=True)
    wallet_address = Column(String)
    sum = Column(Float)
    from_wallet = Column(String)
    to_wallet = Column(String)
    date_of_creation = Column(DateTime, default=datetime.datetime.now())
    owner = Column(StringEncryptedType(String, Data.secret_key, AesEngine),
                   ForeignKey('users.user_id', onupdate="CASCADE", ondelete="CASCADE"))


class UUser(Base):
    __tablename__ = "users"

    user_id = Column(StringEncryptedType(String, Data.secret_key, AesEngine), primary_key=True, unique=True)
    username = Column(StringEncryptedType(String, Data.secret_key, AesEngine))
    datetime_come = Column(DateTime, default=datetime.datetime.now())
    password = Column(StringEncryptedType(String, Data.secret_key, AesEngine), default=None)
    wallets = relationship(
        "Wallet",
        collection_class=attribute_mapped_collection("wallet_address"),
        cascade="all, delete-orphan",
    )

    @classmethod
    async def register(cls, session: AsyncSession, user: User):
        """ someone wants to become a user """
        try:
            stmt = insert(UUser).values(user_id=user.id,
                                        username=user.username)
            do_nothing = stmt.on_conflict_do_nothing(index_elements=['user_id'])
            await session.execute(do_nothing)
            await session.commit()
            result = await session.execute(
                select(UUser).where(
                    UUser.user_id == user.id
                )
            )
            return result.scalars().first()
        except IntegrityError:
            await session.rollback()
            raise

    def __str__(self) -> str:
        return f"User(id={self.user_id!r}, name={self.username!r}, fullname={self.datetime_come!r})"


class Wallet(Base):
    __tablename__ = "wallets"

    wallet_address = Column(StringEncryptedType(String, Data.secret_key, AesEngine), primary_key=True, unique=True)
    blockcain = Column(String)
    network = Column(String)
    date_of_creation = Column(DateTime, default=datetime.datetime.now())
    user = Column(StringEncryptedType(String, Data.secret_key, AesEngine),
                  ForeignKey('users.user_id', onupdate="CASCADE", ondelete="CASCADE"))
