from tronpy import AsyncTron
from tronpy.keys import PrivateKey
from tronpy.exceptions import *
from tronpy.providers.async_http import AsyncHTTPProvider


class Tron_wallet:
    def __init__(self, network: str = 'nile', api_key: str | list[str] | None = None, timeout: float = 10.0):
        self.api_key = api_key
        self.network = network
        self.__fee_limit = 10000000
        self.timeout = timeout

    async def TRX_tron_transfer(self, private_key: str, from_address: str, to_address: str, amount: int):
        priv_key = PrivateKey(bytes.fromhex(private_key))
        async with AsyncTron(network=self.network, provider=AsyncHTTPProvider(api_key=self.api_key)) as client:
            txb = (
                client.trx.transfer(from_address, to_address, amount)
                .with_owner(from_address)
                .fee_limit(self.__fee_limit)

            )
            txn = await txb.build()
            txn_ret = await txn.sign(priv_key).broadcast()
            return await txn_ret.wait()

    async def trc20_transfer(self, private_key: str, contract: str, from_address: str, to_address: str, amount: int):
        print(private_key, contract, from_address, to_address, amount)
        priv_key = PrivateKey(bytes.fromhex(private_key))
        async with AsyncTron(network=self.network, provider=AsyncHTTPProvider(api_key=self.api_key)) as client:
            contract = await client.get_contract(contract)
            txb = await contract.functions.transfer(to_address, amount)
            txb = txb.with_owner(from_address).fee_limit(self.__fee_limit)
            txn = await txb.build()
            txn = txn.sign(priv_key).inspect()
            try:
                txn_ret = await txn.broadcast()
                result = txn_ret.get("result")
                if result is True:
                    return "https://tronscan.org/#/transaction/" + txn_ret.get("txid")
                else:
                    return {"Error": "601"}
                # resul

            except TvmError as er:
                return {"Error": "601", "message": er}
            except Exception as er:
                print("ex_trc20_transfer", er)

    async def get_balance(self, contract: str, address: str):
        try:
            async with AsyncTron(network=self.network, provider=AsyncHTTPProvider(api_key=self.api_key)) as client:
                contract = await client.get_contract(contract)
                return await contract.functions.balanceOf(address)
        except BadAddress as er:
            return {"Error": "701", "message": er}
        except Exception as er:
            return {"Error": "701", "message": f"BadAdress('{address}') OR token not found {er}"}