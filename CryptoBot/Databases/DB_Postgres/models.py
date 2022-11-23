import datetime
import os

import requests
from aiogram.types import User
from sqlalchemy import Column, String, DateTime, ForeignKey, select, BigInteger, Float
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base, relationship, selectinload
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine, StringEncryptedType

from bata import Data

Base = declarative_base()


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(BigInteger, primary_key=True, unique=True, autoincrement=True)
    amount = Column(Float)
    from_wallet = Column(String)
    to_wallet = Column(String)
    date_of_creation = Column(DateTime, default=datetime.datetime.now())
    wallet_addres = Column(StringEncryptedType(String, Data.secret_key, AesEngine),
                           ForeignKey('wallets.wallet_address', onupdate="CASCADE", ondelete="CASCADE"))


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
        wallets: dict = self.wallets
        if blockchain in wallets.keys():
            isExist = True
        if isExist == False:
            APIKEY = os.getenv("API_KEY")  # <-----
            WALLET_ID = os.getenv("WALLET_ID")
            BASE = 'https://rest.cryptoapis.io'
            BLOCKCHAIN = blockchain
            NETWORK = "mainnet"
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
                    f'{BASE}/wallet-as-a-service/wallets/{WALLET_ID}/{BLOCKCHAIN}/{NETWORK}/addresses?context=f{self.id}',
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
    transactions = relationship(
        "Transaction",
        collection_class=attribute_mapped_collection("id"),
        cascade="all, delete-orphan", lazy="joined"
    )

    # async def createTransaction(self,session: AsyncSession, to_wallet: String):

    async def getBalance(self):
        BASE = 'https://apilist.tronscanapi.com/api/accountv2'
        with requests.Session() as httpSession:
            r = httpSession.get(
                f'{BASE}?address=TNcsRFHwCE4qtg3QAujihWk7VY2DezVvKq')
            r.raise_for_status()
            user_tonens = dict()
            for token in r.json().get("withPriceTokens"):
                balance = token.get("balance", "NoneBalance")
                balance = float('{0:,}'.format(int(balance)).replace(',', '.')[:6])
                user_tonens[token.get("tokenName", "NoneName")] = {
                    "tokenType": token.get("tokenType", "NoneType"),
                    "tokenAbbr": token.get("tokenAbbr", "NoneAbbr"),
                    "balance": float(f"{balance:.{3}f}"),
                }
            return user_tonens.items()

    def __str__(self):
        return self.wallet_address
