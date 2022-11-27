from crypto import *
from hdwallet.cryptocurrencies import EthereumMainnet, TronMainnet, BitcoinMainnet


class wallet(Tron_wallet, Eth_wallet, Bitcoin_wallet, Wallet_web3):
    def __init__(self):
        super().__init__()

    async def create_tron_wallet(self, language, strength):
        wallet = Wallet_web3(language, strength)
        await wallet.generate_address(Tron_wallet)
