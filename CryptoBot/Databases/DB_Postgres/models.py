import datetime
import os

import requests
from aiogram.types import User
from sqlalchemy import Column, String, DateTime, ForeignKey, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base, relationship, selectinload
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine, StringEncryptedType

from bata import Data

Base = declarative_base()


# class Transactions(Base):
#     __tablename__ = "receipts"
#
#     ID = Column(BigInteger, primary_key=True, unique=True, autoincrement=True)
#     wallet_address = Column(String)
#     sum = Column(Float)
#     from_wallet = Column(String)
#     to_wallet = Column(String)
#     date_of_creation = Column(DateTime, default=datetime.datetime.now())
#     owner = Column(StringEncryptedType(String, Data.secret_key, AesEngine),
#                    ForeignKey('users.user_id', onupdate="CASCADE", ondelete="CASCADE"))


class Owner(Base):
    __tablename__ = "owners"

    id = Column(StringEncryptedType(String, Data.secret_key, AesEngine), primary_key=True, unique=True)
    username = Column(StringEncryptedType(String, Data.secret_key, AesEngine))
    datetime_come = Column(DateTime, default=datetime.datetime.now())
    password = Column(StringEncryptedType(String, Data.secret_key, AesEngine), default=None)
    wallets = relationship(
        "Wallet",
        collection_class=attribute_mapped_collection("blockchain"),
        cascade="all, delete-orphan", lazy="joined"
    )

    async def createWallet(self, session: AsyncSession, blockchain: str):
        isExist: bool = False
        wallets : dict = self.wallets
        if blockchain in wallets.keys():
            isExist = True
        if isExist == False:
            APIKEY = os.getenv("API_KEY")  # <-----
            WALLET_ID = os.getenv("WALLET_ID")
            BASE = 'https://rest.cryptoapis.io'
            BLOCKCHAIN = blockchain
            NETWORK = "nile"
            data = {
                "context": f"{self.id}",
                "data": {
                    "item": {
                        "label": f"{self.id} - wallet"
                    }
                }
            }
            with requests.Session() as httpSession:
                h = {'Content-Type': 'application/json',
                     'X-API-KEY': APIKEY}
                r = httpSession.post(
                    f'{BASE}/wallet-as-a-service/wallets/{WALLET_ID}/{BLOCKCHAIN}/{NETWORK}/addresses?context=yourExampleString',
                    json=data,
                    headers=h)
                r.raise_for_status()
                wallet_dict = r.json()["data"]["item"]
                wallet: Wallet = Wallet(wallet_address=wallet_dict["address"],
                                        blockchain=BLOCKCHAIN,
                                        network=NETWORK,
                                        user=self.id)

                session.add(wallet)
                await session.commit()
                await session.close()
                return wallet
        else:
            return "У вас уже есть кошелек в данной сети!"

    @staticmethod
    async def register(session: AsyncSession, user: User):
        """ For new users """
        try:
            stmt = insert(Owner).values(id=user.id, username=user.username)
            do_nothing = stmt.on_conflict_do_nothing(index_elements=['id'])
            await session.execute(do_nothing)
            await session.commit()
            return await Owner.get(session, user)
        except IntegrityError:
            await session.rollback()
            raise

    @staticmethod
    async def get(session: AsyncSession, user: User):
        result = await session.execute(
            select(Owner).where(
                Owner.id == user.id
            ).options(selectinload(Owner.wallets)))
        return result.scalars().first()


class Wallet(Base):
    __tablename__ = "wallets"

    wallet_address = Column(StringEncryptedType(String, Data.secret_key, AesEngine), primary_key=True, unique=True)
    blockchain = Column(String)
    network = Column(String)
    date_of_creation = Column(DateTime, default=datetime.datetime.now())
    user = Column(StringEncryptedType(String, Data.secret_key, AesEngine),
                  ForeignKey('owners.id', onupdate="CASCADE", ondelete="CASCADE"))

    def __str__(self):
        return self.wallet_address
