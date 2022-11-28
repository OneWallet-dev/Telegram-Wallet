import datetime
import os

import requests
from aiogram.types import User
from cryptography.hazmat.primitives import hashes
from sqlalchemy import Column, String, DateTime, ForeignKey, select, BigInteger, Float, Table
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base, relationship, selectinload
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine, StringEncryptedType

from Bot.utilts.currency_helper import base_tokens
from bata import Data

Base = declarative_base()

Base_api = 'https://rest.cryptoapis.io'
API_version = "/v2"
Base_api = Base_api + API_version

association_table = Table(
    "address_tokens",
    Base.metadata,
    Column("address_id", ForeignKey("addresses.address"), primary_key=True),
    Column("contract_Id", ForeignKey("tokens.contract_Id"), primary_key=True),
)


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(BigInteger, primary_key=True, unique=True, autoincrement=True)
    mnemonic = Column(String)
    blockchain = Column(String)
    owner_id = Column(String, ForeignKey('owners.id', onupdate="CASCADE", ondelete="CASCADE"))
    addresses = relationship(
        "Address",
        collection_class=attribute_mapped_collection("id"),
        cascade="all, delete-orphan", lazy="joined"
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(BigInteger, primary_key=True, unique=True, autoincrement=True)
    amount = Column(Float)
    from_wallet = Column(String, ForeignKey('addresses.address', onupdate="CASCADE", ondelete="CASCADE"))
    to_wallet = Column(String)
    date_of_creation = Column(DateTime, default=datetime.datetime.now())


class Owner(Base):
    __tablename__ = "owners"

    id = Column(String, primary_key=True, unique=True)
    username = Column(StringEncryptedType(String, Data.secret_key, AesEngine))
    datetime_come = Column(DateTime, default=datetime.datetime.now())
    password = Column(StringEncryptedType(String, Data.secret_key, AesEngine), default=None)
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
            return await Owner.get(session, user)
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
        print(owner)
        wallets: dict[str, Wallet] = owner.wallets
        print(wallets)
        wall = wallets[network]
        wall.tokens.append(Token(token_name=token, contract_Id=base_tokens[token]['contract_address']))
        session.add(wall)
        await session.commit()


class Token(Base):
    __tablename__ = "tokens"

    contract_Id = Column(String, primary_key=True)
    token_name = Column(String)
    addresses = relationship(
        "Address", secondary=association_table, back_populates="tokens", lazy="joined"
    )

    def __str__(self):
        return self.wallet_address

    async def getBalance(self):
        pass


class Address(Base):
    __tablename__ = "addresses"

    address = Column(String, primary_key=True)
    private_key = Column(String)

    wallet_id = Column(BigInteger, ForeignKey('wallets.id', onupdate="CASCADE", ondelete="CASCADE"))

    transactions = relationship(
        "Transaction`",
        collection_class=attribute_mapped_collection("id"),
        cascade="all, delete-orphan", lazy="joined"
    )

    tokens = relationship(
        "Token", secondary=association_table, back_populates="addresses", lazy="joined"
    )

    async def createTransaction(self, session: AsyncSession, to_wallet: str, amount: float):
        pass
