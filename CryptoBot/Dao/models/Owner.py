import datetime
from contextlib import suppress
from string import ascii_letters, digits

from Crypto.Random import random
from aiogram.types import User
from cryptography.hazmat.primitives import hashes
from sqlalchemy import Column, String, DateTime, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection

from Bot.exeptions.wallet_ex import DuplicateToken
from Bot.utilts.currency_helper import base_tokens
from Dao.DB_Postgres.session import create_session, Base
from Dao.models.Address import Address
from Dao.models.Token import Token
from Dao.models.Wallet import Wallet


class Owner(Base):
    __tablename__ = "owners"

    id = Column(String, primary_key=True, unique=True)
    datetime_come = Column(DateTime, default=datetime.datetime.now())
    password = Column(String, default=None)
    wallets: dict[str, Wallet] = relationship(
        "Wallet",
        collection_class=attribute_mapped_collection("blockchain"),
        cascade="all, delete-orphan", lazy="joined"
    )
