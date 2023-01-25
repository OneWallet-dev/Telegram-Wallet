import asyncio
from datetime import datetime
from typing import Union

from hdwallet import BIP44HDWallet
from hdwallet.cryptocurrencies import EthereumMainnet, TronMainnet, BitcoinMainnet, BitcoinTestnet
from hdwallet.derivations import BIP44Derivation

from api.api_exceptions.crypto_exc import MnemonicNotFound
from api.core.security import Security


class AddressGenerator:
    def __init__(self, mnemonic: hex, language: str = "english", strength: int = 256):
        self.__mnemonic = Security().decrypt(mnemonic)
        self.language = language
        self.strength = strength

    async def address(self, cryptocurrency=Union[EthereumMainnet, TronMainnet, BitcoinMainnet, BitcoinTestnet],
                      number_of_addresses: int = 0) -> dict:
        if self.__mnemonic is None:
            raise MnemonicNotFound

        bip44: BIP44HDWallet = BIP44HDWallet(cryptocurrency=cryptocurrency)
        bip44.from_mnemonic(mnemonic=self.__mnemonic)
        bip44.clean_derivation()

        bip44_derivation: BIP44Derivation = BIP44Derivation(
            cryptocurrency=cryptocurrency,
            address=number_of_addresses
        )
        bip44.from_path(path=bip44_derivation)
        return {"address": bip44.address(), "private_key": bip44.private_key(), "wif": bip44.wif()}
