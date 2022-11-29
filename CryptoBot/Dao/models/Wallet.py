from sqlalchemy import Column, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection

from Dao.models.models import Base
from Dao.models.Address import Address


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(BigInteger, primary_key=True, unique=True, autoincrement=True)
    mnemonic = Column(String)
    blockchain = Column(String)
    owner_id = Column(String, ForeignKey('owners.id', onupdate="CASCADE", ondelete="CASCADE"))
    addresses: dict[str, Address] = relationship(
        "Address",
        collection_class=attribute_mapped_collection("address"),
        cascade="all, delete-orphan", lazy="joined"
    )
