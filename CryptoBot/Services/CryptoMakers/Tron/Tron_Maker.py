import os

import requests
from tronpy.keys import PrivateKey
from httpx import AsyncClient, Timeout
from tronpy.defaults import CONF_NILE
from tronpy import AsyncTron
from tronpy.exceptions import BadAddress
from tronpy.providers import AsyncHTTPProvider

from Bot.utilts.settings import DEBUG_MODE
from Dao.models.Address import Address
from Dao.models.Transaction import Transaction
from Services.CryptoMakers.Maker import Maker


class Tron_Maker(Maker):
    def __init__(self):
        self.api_key = os.getenv('tron_API')
        self._main_pk_key = os.getenv('main_private_key')
        self._main_adds = os.getenv('main_address')
        self.signature = None
        self._user_pk_key = None
        self._user_adds = None
        self.owner = None
        self.txn_resp = dict()
        self.energy = 15000
        self.bandwitch = 1000
        self.trx_min_balance = 10
        self.TRON_SCAN_API_URL = "https://apilist.tronscanapi.com/api"
        if DEBUG_MODE:
            self.network = "nile"
        else:
            self.network = "mainnet"
        self._fee_limit = 20_000_000

    def get_client(self):

        if self.network == "mainnet":
            return AsyncTron(provider=AsyncHTTPProvider(api_key=self.api_key, timeout=30))
        elif self.network == "nile":
            _http_client = AsyncClient(timeout=Timeout(timeout=30, connect=5, read=5))
            provider = AsyncHTTPProvider(CONF_NILE, client=_http_client)
            return AsyncTron(provider=provider)

        else:
            raise ValueError(f"network: <{self.network}>  not supported")

    async def account_resource(self, transaction: Transaction):

        async with self.get_client() as client:
            account_resource = await client.get_account_resource(transaction.from_address)
            EnergyUsed = account_resource.get("EnergyUsed", 0)
            EnergyLimit = account_resource.get("EnergyLimit", 0)
            remainde_EnergyUsed = EnergyLimit - EnergyUsed

            freeNetLimit = account_resource.get("freeNetLimit", 0)
            freeNetUsed = account_resource.get("freeNetUsed", 0)
            remainder_freeNetUsed = freeNetLimit - freeNetUsed

            NetUsed = account_resource.get("NetUsed", 0)
            NetLimit = account_resource.get("NetLimit", 0)
            remainder_NetUsed = NetLimit - NetUsed
            BANDWITCH = remainder_freeNetUsed + remainder_NetUsed

            return {
                "ENERGY": remainde_EnergyUsed,
                "BANDWITCH": BANDWITCH
            }

    async def is_valid_address(self, address: str) -> bool:
        try:
            async with self.get_client() as client:
                return client.is_address(address)
        except ValueError:
            return False

    async def is_valid_contract(self, contract_address: str) -> str:
        """
        :param contract_address:
        :return: "contract name"
        """

        async with self.get_client() as client:
            try:
                contract = await client.get_contract(contract_address)
                return contract.name
            except BadAddress:
                return False

    async def freeze(self, amount: float, receiver: str, resource: str = "ENERGY"):
        print("Заморозка трх")
        async with self.get_client() as client:
            txb = client.trx.freeze_balance(
                owner=self._main_adds,
                amount=int(amount * 1_000_000),
                resource=resource,
                receiver=receiver
            )

            try:
                tx = await txb.build()
                p_key = PrivateKey(bytes.fromhex(self._main_pk_key))
                txn_ret = await tx.sign(p_key).broadcast()
                self.txn_resp["txn"] = await txn_ret.wait()
            except Exception as e:
                print(e)
            self.txn_resp["status"] = "ERROR"
            self.txn_resp["message"] = "Freeze failed"

    async def unfreeze(self, receiver: str, resource: str = "ENERGY"):

        async with self.get_client() as client:
            txb = client.trx.unfreeze_balance(
                owner=self._main_adds,
                resource=resource,
                receiver=receiver
            )
        try:
            tx = await txb.build()
            p_key = PrivateKey(bytes.fromhex(self._main_pk_key))
            txn_ret = await tx.sign(p_key).broadcast()
            self.txn_resp["txn"] = await txn_ret.wait()
        except Exception as e:
            print(e)
            self.txn_resp["status"] = "ERROR"
            self.txn_resp["message"] = "Unfreeze failed"

    async def activate_account(self, transaction: Transaction, amount: float = 1):
        async with self.get_client() as client:
            txb = (
                client.trx.transfer(self._main_adds, transaction.from_address, int(1 * 1_000_000))
                .with_owner(self._main_adds)
                .fee_limit(self._fee_limit)
            )
            try:
                tx = await txb.build()
                p_key = PrivateKey(bytes.fromhex(self._main_pk_key))
                txn_ret = await tx.sign(p_key).broadcast()
                print(await txn_ret.wait())

            except Exception as e:
                self.txn_resp["status"] = "ERROR"
                self.txn_resp["message"] = "Activate account failed"
                print("MAIN ACCOUNT ERROR:", e)
            return self

    async def request_transaction_history_from_tron_api(self, address: Address):
        counter = 0
        _http_client = AsyncClient(timeout=Timeout(timeout=30, connect=5, read=5))
        ENDPOINT = "transaction"
        __url = f"{self.TRON_SCAN_API_URL}/{ENDPOINT}?sort=-timestamp&count=true&address={address.address}"
        response = await _http_client.get(__url)
        _http_client.
        response_json = response.json()
        total = response_json["total"]
        transaction_list = response_json["data"]
        transaction_object_list = list()
        print(len(transaction_list))
        for tr in transaction_list:
            my_trans = Transaction()
            my_trans.tnx_id = tr["hash"]
            counter+=1
            print(counter)

