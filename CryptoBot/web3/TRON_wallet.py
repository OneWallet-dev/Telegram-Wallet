from tronpy import AsyncTron
import asyncio
from tronpy.keys import PrivateKey
from tronpy.exceptions import *
from tronpy.providers.async_http import AsyncHTTPProvider

USDT_TRC20 = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"


class Tron_wallet:
    def __init__(self, network: str = 'nile', api_key: str | list[str] | None = None,
                 timeout: float = 10.0):
        self.api_key = api_key
        self.network = network
        self.__fee_limit = 10000000
        self.timeout = timeout
        self.provider = AsyncHTTPProvider(api_key=api_key)

    async def generate_address(self) -> dict:
        async with AsyncTron(network=self.network, provider=self.provider) as client:
            address = client.generate_address()
            wallet = dict()
            wallet['address'] = address.get("base58check_address")
            wallet['hex_address'] = address.get("hex_address")
            wallet['private_key'] = address.get("private_key")
            wallet['public_key'] = address.get("public_key")
            return wallet

    async def TRX_tron_transfer(self, private_key: str, from_address: str, to_address: str, amount: int):
        priv_key = PrivateKey(bytes.fromhex(private_key))
        async with AsyncTron(network=self.network, provider=self.provider) as client:
            txb = (
                client.trx.transfer(from_address, to_address, amount)
                .with_owner(from_address)
                .fee_limit(self.__fee_limit)

            )
            txn = await txb.build()
            txn_ret = await txn.sign(priv_key).broadcast()
            return await txn_ret.wait()

    async def trc20_transfer(self, private_key: str, contract: str, from_address: str, to_address: str, amount: int):
        priv_key = PrivateKey(bytes.fromhex(private_key))
        async with AsyncTron(network=self.network, provider=self.provider) as client:
            contract = await client.get_contract(contract)
            txb = await contract.functions.transfer(to_address, amount)
            txb = txb.with_owner(from_address).fee_limit(self.__fee_limit)
            txn = await txb.build()
            txn = txn.sign(priv_key).inspect()
            try:
                txn_ret = await txn.broadcast()

                # result
                result = await txn_ret.result()
                if result.get("receipt").get("result") == "SUCCESS":
                    return result.get("result")

            except TvmError as er:
                return {"Error": "601", "message": er}
            except Exception as er:
                print("ex_trc20_transfer", er)

    async def get_balance(self, contract: str, address: str):
        try:
            async with AsyncTron(network=self.network, provider=self.provider) as client:
                contract = await client.get_contract(contract)
                return await contract.functions.balanceOf(address)
        except BadAddress as er:
            return {"Error": "701", "message": er}
        except Exception as er:
            return {"Error": "701", "message": f"BadAdress('{address}') OR token not found"}


async def main():
    # example
    tron_wallet = Tron_wallet(network="mainnet", api_key="23ec5f26-fc9d-49e2-8466-a2f1a1d963a7")

    # create tron wallet
    wallet = await tron_wallet.generate_address()
    print(wallet)

    # check usdt balance
    usdt_balance = await tron_wallet.get_balance(USDT_TRC20, wallet.get("address"))
    print(usdt_balance)

    # trx transfer
    await tron_wallet.TRX_tron_transfer(private_key=wallet.get("private_key"), from_address=wallet.get("address"),
                                        to_address="TTetszCQU2E35nS6u6Qaf8MmB2yZbkTe4x", amount=10000)

    # trc20 transfer
    await tron_wallet.trc20_transfer(private_key=wallet.get("private_key"), contract=USDT_TRC20,
                                     from_address=wallet.get("address"),
                                     to_address="TTetszCQU2E35nS6u6Qaf8MmB2yZbkTe4x", amount=10000)


if __name__ == '__main__':
    asyncio.run(main())
