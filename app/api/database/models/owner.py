import datetime

from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection

from api.database.models.wallet import Wallet
from api.database.postgres import Base


class Owner(Base):
    __tablename__ = "owners"

    id = Column(String, primary_key=True)
    password = Column(String)

    created_at = Column(DateTime, default=datetime.datetime.now())

    wallets: dict[str, Wallet] = relationship(
        "Wallet",
        collection_class=attribute_mapped_collection("blockchain"),
        cascade="all, delete-orphan", lazy="joined"
    )
