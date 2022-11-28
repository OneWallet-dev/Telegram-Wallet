import asyncio

from hdwallet import BIP44HDWallet
from hdwallet.cryptocurrencies import EthereumMainnet, TronMainnet, BitcoinMainnet
from hdwallet.derivations import BIP44Derivation
from hdwallet.utils import generate_mnemonic
from typing import Union


class Wallet_web3:
    def __init__(self, language: str = "english", strength: int = 256):
        self.language = language
        self.strength = strength

    async def generate_all_walllets(self, passphrase: str | None = None):
        wallets = dict()
        tron_wallet = await self._generate_address(TronMainnet, passphrase=passphrase)
        eth_wallet = await self._generate_address(TronMainnet, passphrase=passphrase)
        bitcoin_wallet = await self._generate_address(TronMainnet, passphrase=passphrase)
        wallets["tron"] = tron_wallet
        wallets["eth"] = eth_wallet
        wallets["bitcoin"] = bitcoin_wallet
        return wallets

    async def _generate_address(
            self,
            cryptocurrency=Union[EthereumMainnet, TronMainnet, BitcoinMainnet],
            number_of_addresses: int = 1,
            passphrase: str | None = None,
            mnemonic: str = None
    ) -> dict:
        if mnemonic is None:
            mnemonic = generate_mnemonic(language="english", strength=256)

        bip44_hdwallet: BIP44HDWallet = BIP44HDWallet(cryptocurrency=cryptocurrency)
        bip44_hdwallet.from_mnemonic(mnemonic=mnemonic, language=self.language, passphrase=passphrase)
        bip44_hdwallet.clean_derivation()

        wallet = dict()
        wallet["mnemonic"] = mnemonic
        for address_index in range(number_of_addresses):

            bip44_derivation: BIP44Derivation = BIP44Derivation(
                cryptocurrency=cryptocurrency, account=0, change=False, address=address_index
            )
            bip44_hdwallet.from_path(path=bip44_derivation)
            wallet[f"address_{address_index}"] = {"address": bip44_hdwallet.address(), "private_key": bip44_hdwallet.private_key()}

            bip44_hdwallet.clean_derivation()
        return wallet


wallet = Wallet_web3()
print(asyncio.run(wallet.generate_all_walllets()))