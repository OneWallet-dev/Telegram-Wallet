import os
from tronpy import AsyncTron
from tronpy.exceptions import *
from tronpy.keys import PrivateKey
from tronpy.providers.async_http import AsyncHTTPProvider

from Bot.utilts.settings import DEBUG_MODE


class Tron_wallet:
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
        self.__main_fee = 8.4  # будет добавляться эта сумма если недостаточно TRX для перевода
        self.max_user_trx_balance = 14  # если сумма выше данного числа то комиссия добавляться не будет
        self.timeout = 10

    def _get_client(self):
        if self.network == "mainnet":
            print(1)
            return AsyncTron(provider=AsyncHTTPProvider(api_key=self.api_key))
        elif self.network == "nile":
            print(2)
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

    async def TRC_10_get_balance(self, address: str):
        if await self.is_valid_address(address) is False:
            raise ValueError(f"BadAddress {address}")

        client = self._get_client()

        async with client as client:
            return client.get_account_asset_balance()

    async def TRC_20_get_balance(self, contract: str, address: str):
        print(contract)
        print(address)
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
                info = await client.get_transaction(txn_id)
                return info.get("ret")[0].get("contractRet")
            except BadHash:
                req -= 1
                if req == 0:
                    return False
                print("Ожидание", txn_id)
                await self.txn_info(txn_id, req)
            except TransactionNotFound:
                pass

    async def TRC_10_transfer(self, private_key: str, from_address: str, to_address: str, amount: float):
        if await self.is_valid_address(from_address) is False:
            raise ValueError(f"BadFromAddress {from_address}")
        if await self.is_valid_address(to_address) is False:
            print("Адрес получателя указан неверно")
            raise ValueError(f"BadToAddress {to_address}")
        if amount <= 0:
            print("Сумма не может быть ниже нуля")
            raise ValidationError("Amount must be greater than 0")
        trx_balance = await self.TRX_get_balance(from_address)
        if trx_balance < amount:
            print("На счету недостаточно средств")
            raise ValidationError("Balance is not sufficient")

        client = self._get_client()
        priv_key = PrivateKey(bytes.fromhex(private_key))
        async with client as client:
            txb = (
                client.trx.transfer(from_address, to_address, int(amount * 1_000_000))
                .with_owner(from_address)
                .fee_limit(self.__fee_limit)
            )

            txn = await txb.build()
            txn_ret = await txn.sign(priv_key).broadcast()

            return await txn_ret.wait()

    async def __TRX_send_from_main(self, to_address: str, amount: float):
        return await self.TRC_10_transfer(self.main_private_key, self.main_address, to_address, amount)

    async def __additive_trx(self, address, amount: float = None):
        balance_trx = await self.TRX_get_balance(address)
        if float(balance_trx) < float(self.max_user_trx_balance):
            if amount:
                fee = amount
            else:
                fee = self.__main_fee
            await self.__TRX_send_from_main(to_address=address, amount=fee)
            print(f"Добавлена комиссия в размере: {fee} TRX")
            # wait asyncio.sleep(7)

    async def TRC_20_transfer(self, private_key: str, contract: str, from_address: str, to_address: str,
                              amount: float,
                              fee: int = None):
        if await self.is_valid_contract(contract) is False:
            raise ValueError(f"BadContract {contract}")
        if await self.is_valid_address(from_address) is False:
            raise ValueError(f"BadFromAddress {from_address}")
        if await self.is_valid_address(to_address) is False:
            print("Адрес получателя указан неверно")
            raise ValueError(f"BadToAddress {to_address}")

        balance_token = await self.TRC_20_get_balance(contract=contract, address=from_address)
        if float(balance_token) < float(amount):
            return "На счету недостаточно средств"

        balance_trx = await self.TRX_get_balance(address=from_address)
        if balance_trx < self.__main_fee:
            add_fee = self.__main_fee - balance_trx
            print(1, "Не хватает средств для оплаты газа")
            await self.__additive_trx(address=from_address, amount=add_fee)

        client = self._get_client()
        priv_key = PrivateKey(bytes.fromhex(private_key))

        async with client as client:
            contract_f = await client.get_contract(contract)
            txb = await contract_f.functions.transfer(to_address, int(amount * 1_000_000))
            if fee is None:
                fee = self.__fee_limit
            else:
                fee = fee
            txb = txb.with_owner(from_address).fee_limit(fee)
            txn = await txb.build()
            txn = txn.sign(priv_key).inspect()
            try:
                txn_ret = await txn.broadcast()
                txn_id = txn_ret.get("txid")
                txn_info = await self.txn_info(txn_id)
                if txn_info == "SUCCESS":
                    if self.network == "mainnet":
                        return str("https://tronscan.org/#/transaction/" + txn_id)
                    elif self.network == "nile":
                        return str("https://nile.tronscan.org/#/transaction/" + txn_id)
                    print("Успешная транзакция")

                elif txn_info == "OUT_OF_ENERGY":
                    fee += self.__add_fee
                    print(1, "Лимита газа или TRX не достаточно для транзакции")
                    await self.__additive_trx(address=from_address)
                    await self.TRC_20_transfer(private_key, contract, from_address, to_address, amount, fee)
                else:
                    raise ValueError(txn_info)

            except UnknownError:
                print(2, "Не хватает средств для оплаты газа")
                await self.__additive_trx(address=from_address)
                await self.TRC_20_transfer(private_key, contract, from_address, to_address, amount, fee)