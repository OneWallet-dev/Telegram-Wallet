from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from Dao.DB_Postgres.models import Base, association_table


class Token(Base):
    __tablename__ = "tokens"

    contract_Id = Column(String, primary_key=True)
    token_name = Column(String)
    addresses = relationship(
        "Address", secondary=association_table, back_populates="tokens", lazy="joined"
    )

    def __str__(self):
        return self.wallet_address

    async def getBalance(self):
        pass
