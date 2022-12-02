import datetime

from sqlalchemy import Column, BigInteger, Float, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship

from Dao.DB_Postgres.session import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(BigInteger, primary_key=True, unique=True, autoincrement=True)
    tnx_id: str = Column(String)
    token_contract_id = Column(String, ForeignKey('tokens.contract_Id', onupdate="CASCADE", ondelete="CASCADE"))
    amount = Column(Float)
    from_address = Column(String, ForeignKey('addresses.address', onupdate="CASCADE", ondelete="CASCADE"))
    to_address = Column(String)
    datetime = Column(DateTime, default=datetime.datetime.now())
    status:str = Column(String)
    service_fee: float = Column(Float)
    network_fee: float = Column(Float)
    address = relationship("Address", lazy="joined", back_populates="transactions")

    def __str__(self):
        return f"{self.tnx_id}: [{self.amount}]\n{self.from_address} ==>> {self.to_address}\nSTATUS: {self.status}"
    