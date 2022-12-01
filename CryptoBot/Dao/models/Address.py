from sqlalchemy import Column, String, BigInteger, ForeignKey, Integer
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection

from Dao.models.Token import Token
from Dao.models.models import address_tokens
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
        "Token", secondary=address_tokens, back_populates="addresses", lazy="joined"
    )

    token_list = association_proxy("tokens", "contract_Id", creator=lambda tokens: Token(contract_Id=tokens))


    def get_adress_freezed_fee(self) -> float:
        service_fee: float = 0
        for transaction in self.transactions:
            service_fee = +transaction.service_fee

        return service_fee
