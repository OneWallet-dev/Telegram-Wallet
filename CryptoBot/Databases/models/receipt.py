import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, BigInteger, Float

from Databases.DB_Postgres import Base


class receipts(Base):
    __tablename__ = "receipts"

    ID = Column(BigInteger, primary_key=True, unique=True, autoincrement=True)
    wallet_address = Column(String)
    sum = Column(Float)
    from_wallet = Column(String)
    to_wallet = Column(String)
    date_of_creation = Column(DateTime, datetime.datetime.now())
    owner = Column(BigInteger, ForeignKey('users.id'))
