from Dao.models.Transaction import Transaction


class Maker:
    async def transfer(
            self,
            transaction: Transaction,
            service_fee,
            fee_limit: float = None
    ) -> dict:
        pass
