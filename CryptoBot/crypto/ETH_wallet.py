import asyncio
import math
from web3 import Web3, AsyncHTTPProvider
from web3.eth import AsyncEth
from web3.net import AsyncNet
from web3.geth import Geth, AsyncGethTxPool, AsyncGethPersonal, AsyncGethAdmin


class Eth_wallet:
    def __init__(self, api: str, gas_limit: int, cryptocurrency: str = "mainnet"):
        self.__BASE = "https://{}.infura.io/v3/"
        if cryptocurrency == "goerli":
            self.network = self.__BASE.format(cryptocurrency)
        elif cryptocurrency == "mainnet":
            self.network = self.__BASE.format(cryptocurrency)
        else:
            raise ValueError("BadNetwork")
        self.API = api
        self.gas_limit = gas_limit

        self.w3 = Web3(
            AsyncHTTPProvider(self.network + self.API),
            modules={'eth': (AsyncEth,),
                     'net': (AsyncNet,),
                     'geth': (Geth,
                              {'txpool': (AsyncGethTxPool,),
                               'personal': (AsyncGethPersonal,),
                               'admin': (AsyncGethAdmin,)})
                     },
            middlewares=[]  # See supported middleware section below for middleware options
        )

    async def build_txn(self, from_address: str,
                        to_address: str,
                        amount: float,
                        nonce
                        ) -> dict[str, int | str]:

        gas_price = await self.w3.eth.gas_price

        txn = {
            'chainId': await self.w3.eth.chain_id,
            'from': from_address,
            'to': to_address,
            'value': int(Web3.toWei(amount, 'ether')),
            'nonce': nonce,
            'gasPrice': gas_price,
            'gas': self.gas_limit,
        }
        return txn

    async def create_transaction(self, from_address: str,
                                 to_address: str,
                                 amount: float,
                                 private_key: str
                                 ):
        nonce = await self.w3.eth.get_transaction_count(from_address, 'pending')
        try:
            try:
                transaction = await self.build_txn(from_address, to_address, amount, nonce)
                signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)
                txn_hash = await self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            except ValueError:
                nonce += math.ceil(round(nonce / 8, 3))
                print(nonce)
                transaction = await self.build_txn(from_address, to_address, amount, nonce)
                signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)
                txn_hash = await self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

            return txn_hash.hex()
        except ValueError:
            return {'Error': 801, 'message': 'Little gas'}


async def main():
    eth = Eth_wallet(api="854dcd46b0bc46579d3dba0fbfac496c", gas_limit=50_000, cryptocurrency="goerli")
    tr_id = await eth.create_transaction(from_address="0xdd7622DA4742fb8152e6f7DD316fc0BC872FBCdb",
                                         to_address="0xfD8A1C137D6bB676a182A2db9e76f2815A45f083",
                                         amount=0.0000002,
                                         private_key="bba719bdf84c830baa39aa908c7d1dedb80c86b86b7201ffd12f3193b7c4a170")

    print(f"Transfer: ", tr_id)


if __name__ == '__main__':
    asyncio.run(main())
