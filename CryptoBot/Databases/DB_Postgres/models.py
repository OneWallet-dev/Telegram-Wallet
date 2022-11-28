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

from bata import Data

Base = declarative_base()

Base_api = 'https://rest.cryptoapis.io'
API_version = "/v2"
Base_api = Base_api + API_version

association_table = Table(
    "wallets_tokens",
    Base.metadata,
    Column("wallet_id", ForeignKey("wallets.wallet_address"), primary_key=True),
    Column("token_id", ForeignKey("tokens.id"), primary_key=True),
)


class Wallet(Base):
    __tablename__ = "wallets"

    wallet_address = Column(String, primary_key=True, unique=True)
    # TODO: Вероятно устарело
    blockchain = Column(String)
    network = Column(String)

    date_of_creation = Column(DateTime, default=datetime.datetime.now())
    user = Column(String,
                  ForeignKey('owners.id', onupdate="CASCADE", ondelete="CASCADE"))
    addresses = relationship(
        "Address",
        collection_class=attribute_mapped_collection("id"),
        cascade="all, delete-orphan", lazy="joined"
    )

    tokens = relationship(
        "Token", secondary=association_table, back_populates="wallets", lazy="joined"
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(BigInteger, primary_key=True, unique=True, autoincrement=True)
    amount = Column(Float)
    from_wallet = Column(String)
    to_wallet = Column(String)
    date_of_creation = Column(DateTime, default=datetime.datetime.now())
    wallet_address = Column(String,
                            ForeignKey('addresses.id', onupdate="CASCADE", ondelete="CASCADE"))


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
        isExist: bool = False
        wallets: dict = self.wallets
        if blockchain in wallets.keys():
            isExist = True
        if isExist == False:
            APIKEY = os.getenv("API_KEY")  # <-----
            WALLET_ID = os.getenv("WALLET_ID")
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
                    f'{Base_api}/wallet-as-a-service/wallets/{WALLET_ID}/{BLOCKCHAIN}/{NETWORK}/addresses?context=f{self.id}',
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
    async def __generate_wallets(session: AsyncSession, user: User):
        pass

    @staticmethod
    async def get(session: AsyncSession, user: User):
        result = await session.execute(
            select(Owner).where(
                Owner.id == user.id
            ).options(selectinload(Owner.wallets)))
        return result.scalars().first()

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
        owner: Owner = await session.get(Owner.id, str(user.id))
        print(owner)
        wallets: dict[str, Wallet] = Owner.wallets
        for wallet in wallets:
            wall = wallets[wallet]
            wall.tokens.append(Token(token_name=token, contractId=base_tokens[token]['contract_address']))
            session.add(p)
            await session.commit()


class Token(Base):
    __tablename__ = "tokens"

    id = Column(BigInteger, primary_key=True, unique=True, autoincrement=True)
    # TODO: Вероятно устарело
    contractId = Column(String)
    token_name = Column(String)
    wallets = relationship(
        "Wallet", secondary=association_table, back_populates="tokens", lazy="joined"
    )

    def __str__(self):
        return self.wallet_address

    # get_balance from tronscan
    async def getBalance(self):
        BASE = 'https://apilist.tronscanapi.com/api/accountv2'
        with requests.Session() as httpSession:
            r = httpSession.get(
                f'{BASE}?address={self.wallet_address}')
            r.raise_for_status()

            user_tonens = dict()
            for token in r.json().get("withPriceTokens"):
                balance = token.get("balance", "NoneBalance")
                balance = '{0:,}'.format(int(balance)).replace(',', '.')[:6]
                user_tonens[token.get("tokenName", "NoneName")] = {
                    "tokenType": token.get("tokenType", "NoneType"),
                    "tokenAbbr": token.get("tokenAbbr", "NoneAbbr"),
                    "balance": balance
                }
            return user_tonens


class Address(Base):
    __tablename__ = "addresses"

    id = Column(String, primary_key=True, unique=True)
    wallet = Column(String,
                    ForeignKey('wallets.wallet_address', onupdate="CASCADE", ondelete="CASCADE"))
    token = Column(String)
    network = Column(String)

    transactions = relationship(
        "Transaction",
        collection_class=attribute_mapped_collection("id"),
        cascade="all, delete-orphan", lazy="joined"
    )

    async def createTransaction(self, session: AsyncSession, to_wallet: str, amount: float):
        APIKEY = os.getenv("API_KEY")  # <-----
        WALLET_ID = os.getenv("WALLET_ID")
        BLOCKCHAIN = self.blockchain
        NETWORK = "mainnet"
        data = {
            "context": f"{self.wallet_address}",
            "data": {
                "item": {
                    "amount": f"{amount}",
                    "feeLimit": "1000000000",
                    "recipientAddress": f"{to_wallet}",
                    "tokenIdentifier": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
                }
            }
        }
        with requests.Session() as httpSession:
            h = {'Content-Type': 'application/json',
                 'X-API-KEY': APIKEY}
            r = httpSession.post(
                f'{Base_api}/wallet-as-a-service/wallets/{WALLET_ID}/{BLOCKCHAIN}/{NETWORK}/addresses/{self.wallet_address}/feeless-token-transaction-requests',
                json=data,
                headers=h)
            r.raise_for_status()
            transactionRequestId = r.json()["data"]["item"]["transactionRequestId"]
            return f"Ваша транзакция создана. transactionRequestId {transactionRequestId}"
