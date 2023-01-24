from sqlalchemy import Column, String, BigInteger, ForeignKey, Integer
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection


from api.database.models.associations_tables import address_tokens
from api.database.models.transaction import Transaction
from api.database.postgres import Base


class Address(Base):
    __tablename__ = "addresses"

    address = Column(String, primary_key=True)
    wallet_id = Column(BigInteger, ForeignKey('wallets.id', onupdate="CASCADE", ondelete="CASCADE"))

    custom_name = Column(String)
    private_key = Column(String)

    wallet = relationship("Wallet", lazy="joined", back_populates="addresses")

    transactions: dict[int, Transaction] = relationship(
        "Transaction",
        collection_class=attribute_mapped_collection("id"),
        cascade="all, delete-orphan", lazy="joined"
    )
    orders: list[Transaction] = relationship(
        "Transaction",
        cascade="all, delete-orphan", lazy='joined', order_by="Transaction.id"
    )
    tokens = relationship(
        "Token", secondary=address_tokens, back_populates="addresses", lazy="joined"
    )