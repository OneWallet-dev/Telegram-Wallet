import asyncio
import math
from web3 import Web3, AsyncHTTPProvider
from web3.eth import AsyncEth
from web3.net import AsyncNet
from web3.geth import Geth, AsyncGethTxPool, AsyncGethPersonal, AsyncGethAdmin
from ethtoken.abi import EIP20_ABI

mnemonic = "rather movie picnic soft wreck sign dial mango laugh matrix opera below"
wallet_1 = {"address": "0x6f9c2F6f96481848BC39419B53719EAD68FE9F4b",
            "private_key": "0x04e2bfb6457223596d62a1857e65cf745cbfb80eadaaf9d7f967f8ba77f90863"}
wallet_2 = {"address": "0xb1E2e0166AC14769d0688FE4f29eb28f74eD90ea",
            "private_key": "0x2a312af84096ef7184e8e08a8ac0018186911e6038e6fa796b7d83feb200c317"}


class ETH_wallet:

    def __init__(self, network: str = "goerli"):
        self.api_key = "854dcd46b0bc46579d3dba0fbfac496c"
        self.w3 = None
        self.signature = None
        self.txn_resp = dict()
        self.network = network
        self.__add_fee = 500_000
        self.__BASE = "https://{}.infura.io/v3/"
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

    async def build_txn(self, from_address: str,
                        to_address: str,
                        amount: float,
                        nonce,
                        token: str = "ether",
                        contract: str = None
                        ) -> dict[str, int | str]:

        gas_price = await self.get_gas_price()

        if contract is None:
            txn = {
                'chainId': await self.w3.eth.chain_id,
                'from': from_address,
                'to': to_address,
                'value': int(Web3.toWei(amount, token)),
                'nonce': nonce,
                'gasPrice': gas_price,
                'gas': gas_price + self.__add_fee,
            }
            return txn
        else:
            unicorns = self.w3.eth.contract(address=contract, abi=EIP20_ABI)
            nonce = await self.w3.eth.get_transaction_count(from_address, 'pending')

            gas_price = await self.get_gas_price()
            unicorn_txn = unicorns.functions.transfer(
                to_address=to_address,
                amount=amount,
            ).buildTransaction({
                'chainId': 1,
                'gas': gas_price + self.__add_fee,
                'gasPrice': gas_price,
                'nonce': nonce,
            })
            return unicorn_txn

    async def transfer(self, from_address: str,
                       to_address: str,
                       amount: float,
                       private_key: str,
                       contract: str = None
                       ):
        nonce = await self.w3.eth.get_transaction_count(from_address, 'pending')
        if contract is None:
            transaction = await self.build_txn(from_address, to_address, amount, nonce)
            try:
                try:
                    signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)
                    txn_hash = await self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                except ValueError:
                    nonce += math.ceil(round(nonce / 8, 3))

                    signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)
                    txn_hash = await self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

                return txn_hash.hex()
            except ValueError:
                return {'Error': 801, 'message': 'Little gas'}

        else:
            transaction = await self.build_txn(from_address, to_address, amount, nonce, contract)

            signed_txn = self.w3.eth.account.sign_transaction(self.build_txn, private_key=private_key)
            txn_hash = await self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            return txn_hash.hex()





async def main():
    eth = ETH_wallet(network="goerli")
    #tr_id = await eth.transfer(from_address=wallet_1.get("address"),
    #                           to_address=wallet_2.get("address"),
    #                           amount=0.0000001,
    #                           private_key=wallet_1.get("private_key"))

    #print(f"Transfer: ", tr_id)


if __name__ == '__main__':
    asyncio.run(main())