import os

from tronpy import AsyncTron
from tronpy.exceptions import BadAddress
from tronpy.providers import AsyncHTTPProvider

from Bot.utilts.settings import DEBUG_MODE
from CryptoMakers.Maker import Maker


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
        self.fee_limit = 20_000_000  # Максимальный размер газа за транзакцию
        self.add_fee = 5_000_000  # если лимита газа недостаточно для транзакции - будет добавлено данное число к газу
        self.main_fee = 9  # будет добавляться эта сумма если недостаточно TRX для перевода
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