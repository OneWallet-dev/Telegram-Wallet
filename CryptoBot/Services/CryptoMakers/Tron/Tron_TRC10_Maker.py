from tronpy.exceptions import AddressNotFound, ValidationError, BadHash, TransactionNotFound
from tronpy.keys import PrivateKey

from Services.CryptoMakers.Tron.TronMaker import TronMaker
from Dao.DB_Postgres.session import create_session
from Dao.models.Address import Address
from Dao.models.Transaction import Transaction


class Tron_TRC10_Maker(TronMaker):

    async def get_balance(self,
                          address: Address,
                          contract = None) -> float:
        if await self.is_valid_address(address.address) is False:
            raise ValueError(f"BadAddress {address.address}")

        client = self._get_client()

        async with client as client:
            balance =  client.get_account_asset_balance()
            return float(balance)

    async def TRX_get_balance(self, address):
        if await self.is_valid_address(address) is False:
            raise ValueError(f"BadAddress {address}")

        client = self._get_client()

        try:
            async with client as client:
                return float(await client.get_account_balance(address))

        except ValueError:
            print("TRX новый адрес, необходимо активировать")
            return float(0)

        except AddressNotFound:  # активация кошелька
            print(1, "TRX новый адрес, необходимо активировать")
            return float(0)

    async def TRC_10_transfer(self, transaction: Transaction):
        p_key= self.main_private_key
        # p_key = await getPkey_by_address_id(transaction.from_address) TODO разкоментить. В базе будет нормальный кошель
        if await self.is_valid_address(transaction.from_address) is False:
            raise ValueError(f"BadFromAddress {transaction.from_address}")
        if await self.is_valid_address(transaction.to_address) is False:
            print("Адрес получателя указан неверно")
            raise ValueError(f"BadToAddress {transaction.from_address}")
        if transaction.amount <= 0:
            print("Сумма не может быть ниже нуля")
            raise ValidationError("Amount must be greater than 0")
        trx_balance = await self.TRX_get_balance(transaction.from_address)
        if trx_balance < transaction.amount:
            print("На счету недостаточно средств")
            raise ValidationError("Balance is not sufficient")

        client = self._get_client()
        priv_key = PrivateKey(bytes.fromhex(p_key))
        async with client as client:
            txb = (
                client.trx.transfer(transaction.from_address, transaction.to_address, int(transaction.amount * 1_000_000))
                .with_owner(transaction.from_address)
                .fee_limit(self.fee_limit)
            )

            txn = await txb.build()
            txn_ret = await txn.sign(priv_key).broadcast()

            return await txn_ret.wait()


    async def txn_info(self, txn_id, req=5):
        client = self._get_client()
        async with client as client:
            try:
                return await client.get_transaction(txn_id)
            except BadHash:
                req -= 1
                if req == 0:
                    return False
                print("Ожидание", txn_id)
                await self.txn_info(txn_id, req)
            except TransactionNotFound:
                pass


    async def __TRX_send_from_main(self, transaction: Transaction):
        return await self.TRC_10_transfer(transaction)

    async def additive_trx_from_main(self, address:str, amount: float = None):
        session = await create_session()
        async with session() as session:
            trx_transaction = Transaction(tnx_id="from_main", #TODO Научится получать респонс и мапить его на обьект транзакции
                                          token_contract_id = "trx",
                                          to_address=address,
                                          from_address=self.main_address,
                                          status="SUCCESS")
            trx_transaction.from_address = self.main_address
            balance_trx = await self.TRX_get_balance(address)
            if float(balance_trx) < float(self.max_user_trx_balance):
                if amount:
                    trx_transaction.amount = amount
                else:
                    trx_transaction.amount = self.main_fee
                await self.__TRX_send_from_main(trx_transaction)
                session.add(trx_transaction)
                await session.commit()
                await session.close()
                print(f"Добавлена комиссия в размере: {trx_transaction.amount} TRX")
                # wait asyncio.sleep(7)
            else:
                await session.close()