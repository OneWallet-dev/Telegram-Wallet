import json
import math
import os

from web3 import Web3, AsyncHTTPProvider
from web3.eth import AsyncEth
from web3.net import AsyncNet
from web3.geth import Geth, AsyncGethTxPool, AsyncGethPersonal, AsyncGethAdmin
from web3.exceptions import *

from Dao.models.Transaction import Transaction
from Services.CryptoMakers.Maker import Maker

EIP20_ABI = json.loads('[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_from","type":"address"},{"indexed":true,"name":"_to","type":"address"},{"indexed":false,"name":"_value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_owner","type":"address"},{"indexed":true,"name":"_spender","type":"address"},{"indexed":false,"name":"_value","type":"uint256"}],"name":"Approval","type":"event"}]')  # noqa: 501

Polygon_USDT = "0xfe4F5145f6e09952a5ba9e956ED0C25e3Fa4c7F1"


class ETH_maker(Maker):

    def __init__(self): #TODO Здесь зачем network?  Не надо нарушать контрактов. У классасов
        self.api_key = os.getenv('eth_API')
        self.w3 = None
        self.txn_resp = dict()
        self.__gas_limit = 500_000
        self.__BASE = "https://{}.infura.io/v3/"
        self.__get_api_base()
        self.__get_w3()

    def __get_api_base(self):
        # mainnets
        if self.network == "mainnet":  # main eth
            self.__BASE = self.__BASE.format("mainnet")
        elif self.network == "polygon-mainnet":  # main polygon
            self.__BASE = self.__BASE.format("polygon-mainnet")
        elif self.network == "near-mainnet":
            self.__BASE = self.__BASE.format("near-mainnet")
        elif self.network == "arbitrum-mainnet":
            self.__BASE = self.__BASE.format("arbitrum-mainnet")
        elif self.network == "optimism-mainnet":
            self.__BASE = self.__BASE.format("optimism-mainnet")

        # testnets
        elif self.network == "testnet":  # main goerli
            self.__BASE = self.__BASE.format("goerli")
        elif self.network == "polygon-testnet":
            self.__BASE = self.__BASE.format("polygon-mumbai")
        elif self.network == "near-testnet":
            self.__BASE = self.__BASE.format("near-testnet")
        elif self.network == "arbitrum-testnet":
            self.__BASE = self.__BASE.format("arbitrum-goerli")
        elif self.network == "optimism-testnet":  # optimism goerli
            self.__BASE = self.__BASE.format("optimism-goerli")
        else:
            raise ValueError(
                "BadNetwork. The network can be: <mainnet/polygon-mainnet/near-mainnet/arbitrum-mainnet/"
                "optimism-mainnet // testnet/polygon-testnet/near-testnet/arbitrum-testnet/optimism-testnet>"
            )
        return self

    def __get_w3(self):
        self.w3 = Web3(
            AsyncHTTPProvider(self.__BASE + self.api_key),
            modules={'eth': (AsyncEth,),
                     'net': (AsyncNet,),
                     'geth': (Geth,
                              {'txpool': (AsyncGethTxPool,),
                               'personal': (AsyncGethPersonal,),
                               'admin': (AsyncGethAdmin,)})
                     },
            middlewares=[]  # See supported middleware section below for middleware options
        )
        return self

    async def get_transaction_status(self, address):
        try:
            txn = await self.w3.eth.get_transaction_receipt(address)
            if txn.get("status") == 1:
                return txn
            else:
                return False
        except TransactionNotFound:
            print("транзакция не обнаружена")
            return False

    async def get_balance(self, address: str, contract: str = None) -> float:

        if contract:
            contract = self.w3.eth.contract(contract, abi=EIP20_ABI)
            token_decimals_obj = contract.functions.decimals()
            balance_obj = contract.functions.balanceOf(address)

            decimals = await token_decimals_obj.call()
            balance_of_token = await balance_obj.call()
            balance = balance_of_token / 10 ** decimals
            return balance

        elif contract is None:
            balance = await self.w3.eth.get_balance(address)
            return float(self.w3.from_wei(balance, "ether"))

        else:
            raise ValueError("Could not find address")

    async def get_gas_price(self):
        return await self.w3.eth.gas_price  # wei

    async def build_txn(self, transaction: Transaction,
                        nonce
                        ) -> dict[str, int | str]:

        gas_price = await self.get_gas_price()
        print("gas price", self.w3.from_wei(gas_price, "ether"))

        if transaction.token_contract_id is None:
            self.txn_resp["status"] = "Bilded"
            self.txn_resp["message"] = "transaction bilded"
            self.txn_resp["txn"] = None
            txn = {
                'chainId': await self.w3.eth.chain_id,
                'from': transaction.from_address,
                'to': transaction.to_address,
                'value': int(Web3.to_wei(transaction.amount, "ether")),
                'nonce': nonce,
                'gasPrice': gas_price,
                'gas': self.__gas_limit,
            }
        else:

            contract = self.w3.eth.contract(transaction.token_contract_id, abi=EIP20_ABI)
            token_decimals = contract.functions.decimals()
            token_decimals = await token_decimals.call()

            reformat_amount = int(transaction.amount * 10 ** token_decimals)

            nonce = await self.w3.eth.get_transaction_count(transaction.from_address, 'pending')
            self.txn_resp["status"] = "Bilded"
            self.txn_resp["message"] = "transaction bilded"
            self.txn_resp["txn"] = None
            gas_price = await self.get_gas_price()
            txn = await contract.functions.transfer(
                transaction.to_address, reformat_amount
            ).build_transaction({
                'chainId': await self.w3.eth.chain_id,
                'gasPrice': gas_price,
                'gas': self.__gas_limit,
                'nonce': nonce,
            })
        return txn

    async def transfer(self, transaction: Transaction):
        nonce = await self.w3.eth.get_transaction_count(transaction.from_address, 'pending')
        if transaction.token_contract_id is None:
            trn = await self.build_txn(transaction, nonce)

        else:
            trn = await self.build_txn(transaction, nonce)

        try:
            address = transaction.address
            try:
                signed_txn = self.w3.eth.account.sign_transaction(trn, address.private_key)
                txn_hash = await self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            except ValueError:
                nonce += math.ceil(round(nonce / 8, 3))
                signed_txn = self.w3.eth.account.sign_transaction(trn, address.private_key)
                txn_hash = await self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            self.txn_resp["status"] = "SUCCESS"
            self.txn_resp["message"] = "Transfer success"
            self.txn_resp["txn"] = txn_hash.hex()
            return txn_hash.hex()
        except ValueError:
            print("Баланса недостаточно для совершения транзакции")
