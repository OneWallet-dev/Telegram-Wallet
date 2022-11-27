import asyncio

from crypto import Tron_wallet

# example wallet

adress = "TUbRe1onGTTbzotWPhL9spxUu46XaZsuGN"
hex = "41cc4bc9a7475277209ff78b4454f7c53905f1a334"
private_key = "1f54504f6cfa30f295239c1726c1c525579b3cb1ea6186bcf4a2d608a12843b7"
public_key = "b49fedcc8f85b1bb79f2432c2a09857db17b7edaee0cb7656c1f35b83ec38526d0f42db83f4905923a03c7a7c4f52d778452e0b6dba54d94e1116eeca66e7875"


USDT_TRC20 = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"


async def main():
    # example
    tron_wallet = Tron_wallet(network="mainnet", api_key="23ec5f26-fc9d-49e2-8466-a2f1a1d963a7")

    # create tron wallet
    wallet = await tron_wallet.generate_address()
    print(wallet)

    # check usdt balance
    usdt_balance = await tron_wallet.get_balance(USDT_TRC20, wallet.get("address"))
    print(usdt_balance)

    # trc20 transfer
    th_id = await tron_wallet.trc20_transfer(private_key=private_key, contract=USDT_TRC20,
                                     from_address=adress,
                                     to_address="TNcsRFHwCE4qtg3QAujihWk7VY2DezVvKq", amount=10000)
    print(th_id)


if __name__ == '__main__':
    asyncio.run(main())

