from pydantic import ValidationError
from tronpy.exceptions import *
from tronpy.keys import PrivateKey

from CryptoMakers.Tron.TronMaker import TronMaker
from CryptoMakers.Tron.Tron_TRC10_Maker import Tron_TRC10_Maker
from Dao.DB_Postgres.session import create_session
from Dao.models.Address import Address
from Dao.models.Transaction import Transaction


class Tron_TRC20_Maker(TronMaker):

    async def get_balance(self,
                          contract: str,
                          address: str) -> float:#TODO отрефачить это под обьекты!
        if await self.is_valid_address(address) is False:
            raise ValueError(f"BadAddress {address}")
        if await self.is_valid_contract(contract) is False:
            raise ValueError(f"BadContract {contract}")

        client = self._get_client()
        async with client as client:
            contract = await client.get_contract(contract)
            try:
                return float(await contract.functions.balanceOf(address) / 1_000_000)

            except ValueError:
                print(f"'{contract.name}' новый адрес, необходимо активировать")
                return float(0)

            except AddressNotFound:
                print(1, f"'{contract.name}' новый адрес, необходимо активировать")
                return float(0)

    async def transfer(
            self,
            transaction: Transaction,
            fee_limit: float = None
    ) -> dict or None:

        is_contract = await self.is_valid_contract(transaction.token_contract_id)
        if is_contract is False:
            raise ValueError(f"BadContract {transaction.token_contract_id}")
        if await self.is_valid_address(transaction.from_address) is False:
            raise ValueError(f"BadFromAddress {transaction.from_address}")
        if await self.is_valid_address(transaction.to_address) is False:
            print("Адрес получателя указан неверно")
            raise ValueError(f"BadToAddress {transaction.to_address}")

        address = transaction.address
        fee_service_for_transaction = transaction.service_fee
        fee_frozen_on_address = address.get_address_freezed_fee()
        balance_token = await self.get_balance(contract=transaction.token_contract_id, address=transaction.from_address)
        balance_token_avalible_without_fee = balance_token - fee_frozen_on_address
        balance_token_avalible = balance_token_avalible_without_fee - fee_service_for_transaction
        print("balance")
        print(balance_token_avalible)
        if float(balance_token_avalible) < float(transaction.amount):
            return None

        balance_trx = await Tron_TRC10_Maker().TRX_get_balance(address=transaction.from_address)
        if balance_trx < float(self.main_fee):
            add_fee = self.main_fee - balance_trx
            print(1, "Не хватает средств для оплаты газа")
            await Tron_TRC10_Maker().additive_trx_from_main(address=transaction.from_address, amount=add_fee)

        client = self._get_client()
        priv_key = PrivateKey(bytes.fromhex(address.private_key))

        async with client as client:
            contract_f = await client.get_contract(transaction.token_contract_id)
            txb = await contract_f.functions.transfer(transaction.to_address, int(transaction.amount * 1_000_000))
            if fee_limit is None:
                fee_limit = self.fee_limit
            else:
                fee_limit = fee_limit
            txb = txb.with_owner(address.address).fee_limit(fee_limit)
            txn = await txb.build()
            txn = txn.sign(priv_key).inspect()
            try:
                txn_ret = await txn.broadcast()
                txn_id = txn_ret.get("txid")
                print(txn_id)
                txn_info = await Tron_TRC10_Maker().txn_info(txn_id)
                print(111, txn_info)
                status = txn_info.get("ret")[0].get("contractRet")

                print(status)
                if status == "SUCCESS":
                    return {"status": status,
                            "txn_id": txn_id,
                            "contract": transaction.token_contract_id,
                            "from_address": address.address,
                            "to_address": transaction.to_address,
                            "token": is_contract,
                            "amount": transaction.amount,
                            "fee_transaction": fee_service_for_transaction,
                            "fee_frozen": fee_frozen_on_address}

                elif status == "OUT_OF_ENERGY":
                    fee_limit += self.add_fee
                    print(1, "Лимита газа или TRX не достаточно для транзакции")
                    await Tron_TRC10_Maker().additive_trx_from_main(address=address.address, amount=fee_limit)
                    await self.transfer(
                        transaction,
                        fee_limit
                    )
                else:
                    return {"status": status,
                            "txn_id": txn_id}

            except UnknownError:
                print(2, "Не хватает средств для оплаты газа")
                await Tron_TRC10_Maker().additive_trx_from_main(address=address.address, amount=fee_limit)
                await self.transfer(
                    transaction,
                    fee_limit
                )
