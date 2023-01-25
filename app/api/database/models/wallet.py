from sqlalchemy import Column, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection


from api.database.postgres import Base


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(BigInteger, primary_key=True, unique=True, autoincrement=True)
    blockchain = Column(String, ForeignKey('blockchains.name', onupdate="CASCADE", ondelete="CASCADE"))
    owner_id = Column(String, ForeignKey("owners.id"))
    mnemonic = Column(String)

    owner: list = relationship("Owner", lazy="joined", back_populates="wallets")


