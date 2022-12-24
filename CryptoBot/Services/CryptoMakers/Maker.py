from Dao.models.Address import Address
from Dao.models.Token import Token
from Dao.models.Transaction import Transaction


class Maker:
    async def transfer(
            self,
            transaction: Transaction,
    ) -> dict or None:
        pass

    async def get_balance(self,
                          token: Token,
                          address: Address) -> float:
        pass
