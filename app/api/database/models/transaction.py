import datetime

from sqlalchemy import Column, BigInteger, Float, String, ForeignKey, DateTime, Integer
from sqlalchemy.orm import relationship

from api.database.postgres import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(BigInteger, primary_key=True, unique=True, autoincrement=True)
    tnx_id: str = Column(String)
    amount = Column(Float)
    foreign_address = Column(String)

    status: str = Column(String)
    type: str = Column(String)
    service_fee: float = Column(Float)
    network_fee: float = Column(Float)

    created_at = Column(DateTime, default=datetime.datetime.now())

    from_user_id: str = Column(String, ForeignKey('owners.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=True)
    token_id = Column(Integer, ForeignKey('tokens.id', onupdate="CASCADE", ondelete="CASCADE"))

    address = relationship("Address", lazy="joined", back_populates="transactions")
