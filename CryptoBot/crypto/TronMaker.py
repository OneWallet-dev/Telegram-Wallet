import os
from typing import Dict, Any

from pydantic import ValidationError
from sqlalchemy import Column
from sqlalchemy.ext.asyncio import AsyncSession
from tronpy import AsyncTron
from tronpy.exceptions import *
from tronpy.keys import PrivateKey
from tronpy.providers.async_http import AsyncHTTPProvider

from Bot.utilts.p_key_getter import getPkey_by_address_id
from Bot.utilts.settings import DEBUG_MODE
from Dao.DB_Postgres.session import create_session
from Dao.models.Address import Address
from Dao.models.Transaction import Transaction
from crypto.Maker import Maker


class TronMaker(Maker):
    def __init__(self):
        self.api_key = os.getenv('tron_API')
        if DEBUG_MODE:
            self.network = "nile"
        else:
            self.network = "mainnet"
        self.main_address = os.getenv('main_address')
        self.main_private_key = os.getenv('main_private_key')
        # TODO Будем ли мы это брать из базы или конфигурации?
        self.__fee_limit = 20_000_000  # Максимальный размер газа за транзакцию
        self.__add_fee = 5_000_000  # если лимита газа недостаточно для транзакции - будет добавлено данное число к газу
        self.__main_fee = 9  # будет добавляться эта сумма если недостаточно TRX для перевода
        self.max_user_trx_balance = 14  # если сумма выше данного числа то комиссия добавляться не будет
        self.timeout = 10

    def _get_client(self):
        if self.network == "mainnet":
            return AsyncTron(provider=AsyncHTTPProvider(api_key=self.api_key))
        elif self.network == "nile":
            return AsyncTron(network="nile")
        else:
            raise ValueError(f"network: <{self.network}>  not supported")

    async def is_valid_address(self, address: str) -> bool:
        client = self._get_client()

        try:
            async with client as client:
                return client.is_address(address)
        except ValueError:
            return False

    async def is_valid_contract(self, contract_address: str) -> str | bool:
        """
        :param contract_address:
        :return: "contract name"
        """

        client = self._get_client()

        async with client as client:
            try:
                contract = await client.get_contract(contract_address)
                return contract.name
            except BadAddress:
                return False

    async def TRC_10_get_balance(self, address: Address):
        if await self.is_valid_address(address.address) is False:
            raise ValueError(f"BadAddress {address.address}")

        client = self._get_client()

        async with client as client:
            return client.get_account_asset_balance()

    async def TRC_20_get_balance(self, contract: str, address: str):
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
                pass

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
                .fee_limit(self.__fee_limit)
            )

            txn = await txb.build()
            txn_ret = await txn.sign(priv_key).broadcast()

            return await txn_ret.wait()

    async def __TRX_send_from_main(self, transaction: Transaction):
        return await self.TRC_10_transfer(transaction)

    async def __additive_trx_from_main(self, address:str, amount: float = None):
        session = await create_session()
        async with session() as session:
            trx_transaction = Transaction(tnx_id="from_main", #TODO Научится получать респонс и мапить его на обьект транзакции
                                          token_contract_id = "trx",
                                          to_address=address,
                                          from_address=self.main_address,
                                          status="False")
            trx_transaction.from_address = self.main_address
            balance_trx = await self.TRX_get_balance(address)
            if float(balance_trx) < float(self.max_user_trx_balance):
                if amount:
                    trx_transaction.amount = amount
                else:
                    trx_transaction.amount = self.__main_fee
                await self.__TRX_send_from_main(trx_transaction)
                session.add(trx_transaction)
                await session.commit()
                await session.close()
                print(f"Добавлена комиссия в размере: {trx_transaction.amount} TRX")
                # wait asyncio.sleep(7)
            else:
                await session.close()

    async def transfer(
            self,
            transaction: Transaction,
            service_fee,
            fee_limit: float = None
    ) -> dict or None:

        """
        :param private_key: from owner address
        :param contract_address: token contract
        :param from_address: owner address
        :param to_address: address of the recipient
        :param amount: amount sent
        :param fee_service_for_transaction: service commission
        :param fee_frozen_on_address: frozen owner balance
        :param fee_limit: it is advisable not to touch the technical parameter
        :return: private_key, contract_address, from_address, to_address, amount, fee_transaction, fee_frozen, fee_limit
        """
        is_contract = await self.is_valid_contract(transaction.token_contract_id)
        if is_contract is False:
            raise ValueError(f"BadContract {transaction.token_contract_id}")
        if await self.is_valid_address(transaction.from_address) is False:
            raise ValueError(f"BadFromAddress {transaction.from_address}")
        if await self.is_valid_address(transaction.to_address) is False:
            print("Адрес получателя указан неверно")
            raise ValueError(f"BadToAddress {transaction.to_address}")

        address = transaction.address
        fee_service_for_transaction = service_fee
        fee_frozen_on_address = address.get_address_freezed_fee()
        balance_token = await self.TRC_20_get_balance(contract=transaction.token_contract_id, address=transaction.from_address)
        balance_token_avalible_without_fee = balance_token - fee_frozen_on_address
        balance_token_avalible = balance_token_avalible_without_fee - fee_service_for_transaction
        print("balance")
        print(balance_token_avalible)
        if float(balance_token_avalible) < float(transaction.amount):
            return None

        balance_trx = await self.TRX_get_balance(address=transaction.from_address)
        if balance_trx < float(self.__main_fee):
            add_fee = self.__main_fee - balance_trx
            print(1, "Не хватает средств для оплаты газа")
            await self.__additive_trx_from_main(address=transaction.from_address, amount=add_fee)

        client = self._get_client()
        priv_key = PrivateKey(bytes.fromhex(address.private_key))

        async with client as client:
            contract_f = await client.get_contract(transaction.token_contract_id)
            txb = await contract_f.functions.transfer(transaction.to_address, int(transaction.amount * 1_000_000))
            if fee_limit is None:
                fee_limit = self.__fee_limit
            else:
                fee_limit = fee_limit
            txb = txb.with_owner(address.address).fee_limit(fee_limit)
            txn = await txb.build()
            txn = txn.sign(priv_key).inspect()
            try:
                txn_ret = await txn.broadcast()
                txn_id = txn_ret.get("txid")
                print(txn_id)
                txn_info = await self.txn_info(txn_id)
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
                    fee_limit += self.__add_fee
                    print(1, "Лимита газа или TRX не достаточно для транзакции")
                    await self.__additive_trx_from_main(address=address.address, amount=fee_limit)
                    await self.transfer(
                        transaction,
                        fee_limit
                    )
                else:
                    return {"status": status,
                            "txn_id": txn_id}

            except UnknownError:
                print(2, "Не хватает средств для оплаты газа")
                await self.__additive_trx_from_main(address=address.address,amount=fee_limit)
                await self.transfer(
                    transaction,
                    fee_limit
                )
