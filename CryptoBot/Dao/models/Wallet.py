from sqlalchemy import Column, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy_utils import StringEncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

from Dao.DB_Postgres.session import Base
from bata import Data


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(BigInteger, primary_key=True, unique=True, autoincrement=True)
    mnemonic = Column(StringEncryptedType(String, Data.secret_key, AesEngine))
    blockchain = Column(String)
    owner_id = Column(StringEncryptedType(String, Data.secret_key, AesEngine),
                      ForeignKey('owners.id', onupdate="CASCADE", ondelete="CASCADE"))
    addresses = relationship(
        "Address",
        collection_class=attribute_mapped_collection("address"),
        cascade="all, delete-orphan", lazy="joined"
    )
    owner = relationship("Owner", lazy="joined", back_populates="wallets")
