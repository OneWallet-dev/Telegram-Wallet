import os
from tronpy import AsyncTron
from tronpy.exceptions import *
from tronpy.keys import PrivateKey
from tronpy.providers.async_http import AsyncHTTPProvider

from Bot.utilts.settings import DEBUG_MODE
from Services.address_service import AdressService


class Tron_wallet(AdressService):
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
                return await client.get_transaction(txn_id)
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

    async def TRC_20_transfer(
            self,
            private_key: str,
            contract_address: str,
            from_address: str,
            to_address: str,
            amount: float,
            fee_transaction: float = None,
            fee_frozen: float = None,
            fee_limit: int = None
    ) -> dict:

        """
        :param private_key: from owner address
        :param contract_address: token contract
        :param from_address: owner address
        :param to_address: address of the recipient
        :param amount: amount sent
        :param fee_transaction: service commission
        :param fee_frozen: frozen owner balance
        :param fee_limit: it is advisable not to touch the technical parameter
        :return: private_key, contract_address, from_address, to_address, amount, fee_transaction, fee_frozen, fee_limit
        """
        is_contract = await self.is_valid_contract(contract_address)
        if is_contract is False:
            raise ValueError(f"BadContract {contract_address}")
        if await self.is_valid_address(from_address) is False:
            raise ValueError(f"BadFromAddress {from_address}")
        if await self.is_valid_address(to_address) is False:
            print("Адрес получателя указан неверно")
            raise ValueError(f"BadToAddress {to_address}")

        balance_token = await self.TRC_20_get_balance(contract=contract_address, address=from_address)
        balance_token = balance_token - fee_transaction
        balance_token = balance_token - fee_frozen

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
            contract_f = await client.get_contract(contract_address)
            txb = await contract_f.functions.transfer(to_address, int(amount * 1_000_000))
            if fee_limit is None:
                fee_limit = self.__fee_limit
            else:
                fee_limit = fee_limit
            txb = txb.with_owner(from_address).fee_limit(fee_limit)
            txn = await txb.build()
            txn = txn.sign(priv_key).inspect()
            try:
                txn_ret = await txn.broadcast()
                txn_id = txn_ret.get("txid")
                txn_info = await self.txn_info(txn_id)
                status = txn_info.get("ret")[0].get("contractRet")
                if status == "SUCCESS":
                    return {"status": status,
                            "txn_id": txn_id,
                            "contract": contract_address,
                            "from_address": from_address,
                            "to_address": to_address,
                            "token": is_contract,
                            "amount": amount,
                            "fee_transaction": fee_transaction,
                            "fee_frozen": fee_frozen}

                elif status == "OUT_OF_ENERGY":
                    fee_limit += self.__add_fee
                    print(1, "Лимита газа или TRX не достаточно для транзакции")
                    await self.__additive_trx(address=from_address)
                    await self.TRC_20_transfer(
                        private_key,
                        contract_address,
                        from_address,
                        to_address,
                        amount,
                        fee_transaction,
                        fee_frozen,
                        fee_limit
                    )
                else:
                    return {"status": status,
                            "txn_id": txn_id}

            except UnknownError:
                print(2, "Не хватает средств для оплаты газа")
                await self.__additive_trx(address=from_address)
                await self.TRC_20_transfer(
                    private_key,
                    contract_address,
                    from_address,
                    to_address,
                    amount,
                    fee_transaction,
                    fee_frozen,
                    fee_limit
                )
