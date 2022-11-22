import datetime

from sqlalchemy import Column, BigInteger, String, Float, DateTime, ForeignKey, Integer, Table
from sqlalchemy.orm import declarative_base
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine, EncryptedType, StringEncryptedType

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


class Users(Base):
    __tablename__ = "users"

    user_id = Column(StringEncryptedType(String, Data.secret_key, AesEngine), primary_key=True, unique=True)
    username = Column(StringEncryptedType(String, Data.secret_key, AesEngine))
    datetime_come = Column(DateTime, default=datetime.datetime.now())
    password = Column(StringEncryptedType(String, Data.secret_key, AesEngine), default=None)

    def __str__(self) -> str:
        return f"User(id={self.user_id!r}, name={self.username!r}, fullname={self.datetime_come!r})"


class Wallets(Base):
    __tablename__ = "wallets"

    wallet_address = Column(StringEncryptedType(String, Data.secret_key, AesEngine), primary_key=True, unique=True)
    blockcain = Column(String)
    network = Column(String)
    date_of_creation = Column(DateTime, default=datetime.datetime.now())
    user = Column(StringEncryptedType(String, Data.secret_key, AesEngine),
                  ForeignKey('users.user_id', onupdate="CASCADE", ondelete="CASCADE"))
