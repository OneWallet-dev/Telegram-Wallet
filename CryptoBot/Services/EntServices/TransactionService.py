from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.ext.asyncio import AsyncSession

from Dao.DB_Postgres.session import AlchemyMaster
from Dao.models.Address import Address
from Dao.models.Token import Token
from Dao.models.Transaction import Transaction


class TransactionService:

    @staticmethod
    @AlchemyMaster.alchemy_session
    async def create_transaction(token: Token, owner_address: str, foreign_address: str, amount: float,
                                 fee: float, transaction_type: str,
                                 *,
                                 alchemy_session: AsyncSession):
        assert transaction_type in ['sending', 'receiving'], 'Transaction type must be "sending" or "receiving"!'

        owner_address_obj: Address = await alchemy_session.get(Address, owner_address)
        if not owner_address_obj:
            raise Exception(f'Cant find address {owner_address} in base!')

        foreign_address_obj: Address = await alchemy_session.get(Address, foreign_address)
        if foreign_address_obj:
            foreign_owner_uid = foreign_address_obj.wallet.owner_id
        else:
            foreign_owner_uid = None

        transaction = Transaction(token=token,
                                 amount=amount,
                                 foreign_address=foreign_address,
                                 address=owner_address_obj,
                                 service_fee=fee,
                                 type=transaction_type,
                                 foreign_related_UID=foreign_owner_uid
        )
        return transaction
