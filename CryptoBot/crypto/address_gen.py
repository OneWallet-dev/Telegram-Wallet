from hdwallet import BIP44HDWallet
from hdwallet.cryptocurrencies import EthereumMainnet, TronMainnet, BitcoinMainnet
from hdwallet.derivations import BIP44Derivation
from hdwallet.utils import generate_mnemonic
from typing import Union


class Wallet_web3:
    def __init__(self, language: str = "english", strength: int = 256):
        self.language = language
        self.strength = strength

    async def generate_address(
            self,
            cryptocurrency=Union[EthereumMainnet, TronMainnet, BitcoinMainnet],
            number_of_addresses: int = 1,
            passphrase: str | None = None
    ) -> dict:
        mnemonic = generate_mnemonic(language="english", strength=256)
        bip44_hdwallet: BIP44HDWallet = BIP44HDWallet(cryptocurrency=cryptocurrency)
        bip44_hdwallet.from_mnemonic(mnemonic=mnemonic, language=self.language, passphrase=passphrase)
        bip44_hdwallet.clean_derivation()

        wallet = dict()
        for address_index in range(number_of_addresses):

            bip44_derivation: BIP44Derivation = BIP44Derivation(
                cryptocurrency=cryptocurrency, account=0, change=False, address=address_index
            )
            bip44_hdwallet.from_path(path=bip44_derivation)
            wallet["address"] = bip44_hdwallet.address()
            wallet["private_key"] = bip44_hdwallet.private_key()

            bip44_hdwallet.clean_derivation()
        return wallet
