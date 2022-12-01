from Dao.DB_Postgres.session import create_session
from Dao.models.Address import Address
from Dao.models.Token import Token
from Dao.models.Transaction import Transaction
from crypto.TRON_wallet import Tron_wallet


class AdressService:

    # REFACTORING 1
    @staticmethod
    async def get_balances(address: str, specific: list[Token] | None = None):
        session_connect = await create_session()
        async with session_connect() as session:
            address_obj: Address = await session.get(Address, address)
            balances = dict()
            twallet = Tron_wallet()
            for token in address_obj.tokens:
                if (specific and token in specific) or not specific:
                    if token.token_name == 'TRX':
                        balance = await twallet.TRX_get_balance(address)
                    elif token.network == 'TRC-20':
                        balance = await twallet.TRC_20_get_balance(token.contract_Id, address)
                    elif token.network == 'TRC-10':
                        balance = await twallet.TRC_10_get_balance(address)
                    balances.update({token.token_name: balance})
        return balances

    @staticmethod
    async def createTransaction(adress: Address, amount: float) -> Transaction:
        await Tron_wallet.TRC_20_transfer()


        return Transaction()