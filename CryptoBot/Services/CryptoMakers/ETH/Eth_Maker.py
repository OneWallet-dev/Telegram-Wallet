import asyncio
import math
from web3 import Web3, AsyncHTTPProvider
from web3.eth import AsyncEth
from web3.net import AsyncNet
from web3.geth import Geth, AsyncGethTxPool, AsyncGethPersonal, AsyncGethAdmin
from ethtoken.abi import EIP20_ABI

from Bot.utilts.settings import DEBUG_MODE
from Dao.models.Transaction import Transaction
from Services.CryptoMakers.Maker import Maker

mnemonic = "rather movie picnic soft wreck sign dial mango laugh matrix opera below"
wallet_1 = {"address": "0x6f9c2F6f96481848BC39419B53719EAD68FE9F4b",
            "private_key": "0x04e2bfb6457223596d62a1857e65cf745cbfb80eadaaf9d7f967f8ba77f90863"}
wallet_2 = {"address": "0xb1E2e0166AC14769d0688FE4f29eb28f74eD90ea",
            "private_key": "0x2a312af84096ef7184e8e08a8ac0018186911e6038e6fa796b7d83feb200c317"}


class ETH_wallet(Maker):

    def __init__(self):
        self.api_key = "854dcd46b0bc46579d3dba0fbfac496c"
        self.w3 = None
        self.signature = None
        self.txn_resp = dict()
        self.__add_fee = 500_000
        self.__BASE = "https://{}.infura.io/v3/"

        if DEBUG_MODE:
            self.network = "goerli"
        else:
            self.network = "mainnet"

        self.__get_api_base()
        self.__get_w3()

    def __get_api_base(self):
        if self.network == "goerli":
            self.__BASE = self.__BASE.format(self.network)
        elif self.network == "mainnet":
            self.__BASE = self.__BASE.format(self.network)
        else:
            raise ValueError("BadNetwork")
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

    def __is_valid_token(self, token_name):
        token_list = [
            'wei', 'kwei', 'babbage', 'femtoether', 'mwei', 'lovelace',
            'picoether', 'gwei', 'shannon', 'nanoether', 'nano', 'szabo',
            'microether', 'micro', 'finney', 'milliether', 'milli', 'ether',
            'kether', 'grand', 'mether', 'gether', 'tether'
        ]
        if token_name in token_list:
            return True
        else:
            return False

    async def get_gas_price(self):
        return await self.w3.eth.gas_price

    async def get_balance(self, address, contract):
        balance = await self.w3.eth.get_balance(address)
        return self.w3.fromWei(balance, "ether")

    async def build_txn(self, transaction: Transaction, nonce) -> dict[str, int | str]:

        gas_price = await self.get_gas_price()

        if transaction.token_contract_id is None:
            txn = {
                'chainId': await self.w3.eth.chain_id,
                'from': transaction.from_address,
                'to': transaction.to_address,
                'value': int(Web3.toWei(transaction.amount, "ether")),
                'nonce': nonce,
                'gasPrice': gas_price,
                'gas': gas_price + self.__add_fee,
            }
            return txn
        else:
            unicorns = self.w3.eth.contract(address=transaction.token_contract_id, abi=EIP20_ABI)
            nonce = await self.w3.eth.get_transaction_count(transaction.from_address, 'pending')

            gas_price = await self.get_gas_price()
            unicorn_txn = unicorns.functions.transfer(
                to_address=transaction.to_address,
                amount=transaction.amount,
            ).buildTransaction({
                'chainId': 1,
                'gas': gas_price + self.__add_fee,
                'gasPrice': gas_price,
                'nonce': nonce,
            })
            return unicorn_txn

    async def transfer(self, transaction: Transaction):
        nonce = await self.w3.eth.get_transaction_count(transaction.from_address, 'pending')
        address = transaction.address
        if transaction.token_contract_id is None:
            try:
                try:
                    txn = await self.build_txn(transaction, nonce)
                    signed_txn = self.w3.eth.account.sign_transaction(txn, address.private_key)
                    txn_hash = await self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                except ValueError:
                    nonce += math.ceil(round(nonce / 8, 3))
                    txn = await self.build_txn(transaction, nonce)
                    signed_txn = self.w3.eth.account.sign_transaction(txn, address.private_key)
                    txn_hash = await self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                print("Transfer", txn_hash)
                self.txn_resp["status"] = "SUCCESS"
                self.txn_resp["message"] = "Transfer success"
                self.txn_resp["txn"] = await txn_hash.hex()
                return txn_hash.hex()
            except ValueError:
                return {'Error': 801, 'message': 'Little gas'}

        else:
            print("ERC-20 Токены не готовы")
            #signed_txn = self.w3.eth.account.sign_transaction(self.build_txn, private_key=private_key)
            #txn_hash = await self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            #return txn_hash.hex()