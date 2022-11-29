import asyncio

from aiogram.types import Message
from hdwallet import BIP44HDWallet
from hdwallet.cryptocurrencies import EthereumMainnet, TronMainnet, BitcoinMainnet
from hdwallet.derivations import BIP44Derivation
from hdwallet.utils import generate_mnemonic
from typing import Union

from sqlalchemy.ext.asyncio import AsyncSession

from Dao.models import Address, Owner, Wallet


class Wallet_web3:
    def __init__(self, language: str = "english", strength: int = 256):
        self.language = language
        self.strength = strength

    async def generate_all_walllets(self, user_id: int, session: AsyncSession, passphrase: str | None = None):
        wallets = dict()
        tron_wallet = await self._generate_address(TronMainnet, passphrase=passphrase)
        tron_mnemomic = tron_wallet.get("mnemonic")
        eth_wallet = await self._generate_address(EthereumMainnet, passphrase=passphrase)
        eth_mnemomic = eth_wallet.get("mnemonic")
        bitcoin_wallet = await self._generate_address(BitcoinMainnet, passphrase=passphrase)
        bitcoin_mnemomic = bitcoin_wallet.get("mnemonic")
        print(bitcoin_mnemomic)

        owner: Owner = await session.get(Owner, str(user_id))
        tronaddress: Address = Address(address=tron_wallet.get("address_0").get("address"),
                                       private_key=tron_wallet.get("address_0").get("private_key"))
        tronwallet = Wallet(blockchain="tron", mnemonic=tron_mnemomic)
        tronwallet.addresses.update({tron_wallet.get("address_0").get("address"): tronaddress})
        owner.wallets["tron"] = tronwallet

        ethaddress: Address = Address(address=eth_wallet.get("address_0").get("address"),
                                      private_key=eth_wallet.get("address_0").get("private_key"))
        ethnwallet = Wallet(blockchain="ethereum", mnemonic=eth_mnemomic)
        ethnwallet.addresses.update({eth_wallet.get("address_0").get("address"): ethaddress})
        owner.wallets["ethereum"] = ethnwallet

        bitaddress: Address = Address(address=bitcoin_wallet.get("address_0").get("address"),
                                      private_key=bitcoin_wallet.get("address_0").get("private_key"))
        bitwallet = Wallet(blockchain="bitcoin", mnemonic=bitcoin_mnemomic)
        bitwallet.addresses.update({bitcoin_wallet.get("address_0").get("address"): bitaddress})
        owner.wallets["bitcoin"] = bitwallet

        session.add(owner)
        await session.commit()
        await session.close()
        try:
            wallets['tron'] = list(owner.wallets.get("tron").addresses.keys())[0]
            wallets['eth'] = list(owner.wallets.get("ethereum").addresses.keys())[0]
            wallets['bitcoin'] = list(owner.wallets.get("bitcoin").addresses.keys())[0]
        except:
            print("Кошельки не создались")
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