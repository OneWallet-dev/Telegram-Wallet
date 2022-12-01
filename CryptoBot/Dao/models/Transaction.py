import datetime

from sqlalchemy import Column, BigInteger, Float, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship

from Dao.DB_Postgres.session import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(BigInteger, primary_key=True, unique=True, autoincrement=True)
    tnx_id: str = Column(String)
    token_name = relationship(
        "Token", lazy="joined"
    )
    amount = Column(Float)
    from_wallet = Column(String, ForeignKey('addresses.address', onupdate="CASCADE", ondelete="CASCADE"))
    to_wallet = Column(String)
    datetime = Column(DateTime, default=datetime.datetime.now())
    status:bool = Column(Boolean)
    service_fee: float = Column(Float)
    network_fee: float = Column(Float)
