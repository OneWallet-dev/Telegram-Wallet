from sqlalchemy import Column, String, BigInteger, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection

from Dao.models.models import association_table, Base
from Dao.models.Transaction import Transaction

class Address(Base):
    __tablename__ = "addresses"

    address = Column(String, primary_key=True)
    private_key = Column(String)

    wallet_id = Column(BigInteger, ForeignKey('wallets.id', onupdate="CASCADE", ondelete="CASCADE"))

    transactions = relationship(
        "Transaction",
        collection_class=attribute_mapped_collection("id"),
        cascade="all, delete-orphan", lazy="joined"
    )

    tokens = relationship(
        "Token", secondary=association_table, back_populates="addresses", lazy="joined"
    )

    async def createTransaction(self, session: AsyncSession, to_wallet: str, amount: float):
        pass
