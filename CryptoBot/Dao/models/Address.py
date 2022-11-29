from sqlalchemy import Column, String, BigInteger, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection

from Dao.models.models import association_table
from Dao.DB_Postgres.session import Base
from Dao.models.Transaction import Transaction

class Address(Base):
    __tablename__ = "addresses"

    address = Column(String, primary_key=True)
    private_key = Column(String)
    path_index = Column(Integer, default=0)

    wallet_id = Column(BigInteger, ForeignKey('wallets.id', onupdate="CASCADE", ondelete="CASCADE"))

    transactions: dict[int: Transaction] = relationship(
        "Transaction",
        collection_class=attribute_mapped_collection("id"),
        cascade="all, delete-orphan", lazy="joined"
    )

    tokens = relationship(
        "Token", secondary=association_table, back_populates="addresses", lazy="joined"
    )
