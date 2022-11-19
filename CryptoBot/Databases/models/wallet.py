import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, BigInteger

from Databases.DB_Postgres import Base


class Wallets(Base):
    __tablename__ = "wallets"

    mnemonic = Column(String, primary_key=True, unique=True, autoincrement=False)
    wallet_address = Column(String)
    public_key = Column(String)
    network = Column(String)
    date_of_creation = Column(DateTime, datetime.datetime.now())
    owner = Column(BigInteger, ForeignKey('users.id'))

