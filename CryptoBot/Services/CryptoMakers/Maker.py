from tronpy import AsyncTron
from tronpy.providers import AsyncHTTPProvider

from Dao.models.Address import Address
from Dao.models.Transaction import Transaction


class Maker:
    async def transfer(
            self,
            transaction: Transaction,
    ) -> dict or None:
        pass

    async def get_balance(self,
                          contract: str,
                          address: Address) -> float:
        pass
