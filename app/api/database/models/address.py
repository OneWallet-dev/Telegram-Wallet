from sqlalchemy import Column, String, BigInteger, ForeignKey, Integer
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection


from api.database.models.transaction import Transaction
from api.database.postgres import Base


class Address(Base):
    __tablename__ = "addresses"

    address = Column(String, primary_key=True)
    custom_name = Column(String)
    address_index = Column(Integer)

    wallet_id = Column(BigInteger, ForeignKey('wallets.id', onupdate="CASCADE", ondelete="CASCADE"))
