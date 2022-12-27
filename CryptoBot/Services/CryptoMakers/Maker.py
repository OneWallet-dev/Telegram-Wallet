from Dao.models.Address import Address
from Dao.models.Token import Token
from Dao.models.Transaction import Transaction


class Maker:

    async def init_client(self, transaction: Transaction = None, token: Token = None, address: Address = None):
        pass

    async def transfer(self) -> dict or None:
        pass

    async def get_balance(self) -> float:
        pass
