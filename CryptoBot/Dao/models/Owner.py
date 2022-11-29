import datetime

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
    username = Column(String)
    datetime_come = Column(DateTime, default=datetime.datetime.now())
    password = Column(String, default=None)
    wallets: dict[str: Wallet] = relationship(
        "Wallet",
        collection_class=attribute_mapped_collection("blockchain"),
        cascade="all, delete-orphan", lazy="joined"
    )

    async def createWallet(self, session: AsyncSession, blockchain: str):
        pass

    @staticmethod
    async def register(session: AsyncSession, user: User, password: str | None = None):
        """ For new users """
        password = Owner._password_encode(password)
        try:
            stmt = insert(Owner).values(id=str(user.id), username=user.username, password=password)
            do_nothing = stmt.on_conflict_do_nothing(index_elements=['id'])
            await session.execute(do_nothing)
            await session.commit()
            return await session.get(Owner, str(user.id))
        except IntegrityError:
            await session.rollback()
            raise

    @staticmethod
    async def password_check(session: AsyncSession, user: User, text: str):
        owner: Owner = await session.get(Owner, str(user.id))
        phash = Owner._password_encode(text)
        return True if owner.password == phash else False

    @staticmethod
    def _password_encode(text: str):
        digest = hashes.Hash(hashes.SHA256())
        digest.update(bytes(text, "UTF-8"))
        result = digest.finalize()
        return str(result)

    @staticmethod
    async def add_currency(user: User, token: str, network: str):
        session_connect = await create_session()
        async with session_connect() as session:
            token_ref = base_tokens.get(token)

            address = await Owner.get_address(session, user, token_ref['blockchain'])
            token_obj = Token(token_name=token,
                              contract_Id=base_tokens[token]['contract_address'],
                              network=network)
            if token_obj not in address.tokens:
                address.tokens.append(token_obj)
                session.add(address)
                await session.commit()
            else:
                raise DuplicateToken

    @staticmethod
    async def get_address(session: AsyncSession, user: User, blockchain: str, path_index: int = 0):
        address: Address = (await session.execute(
            select(Address).where(
                Address.path_index == path_index, Address.wallet_id == select(Wallet.id).where(
                    Wallet.owner_id == str(user.id), Wallet.blockchain == blockchain).scalar_subquery()))
                            ).first()[0]
        return address
