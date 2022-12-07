from aiogram.types import Message
from hdwallet import BIP44HDWallet
from hdwallet.cryptocurrencies import EthereumMainnet, TronMainnet, BitcoinMainnet
from hdwallet.derivations import BIP44Derivation
from hdwallet.utils import generate_mnemonic
from typing import Union
from sqlalchemy.ext.asyncio import AsyncSession

from Dao.DB_Postgres.session import create_session, AlchemyMaster
from Dao.models.Address import Address
from Dao.models.Owner import Owner
from Dao.models.Wallet import Wallet


class Wallet_web3:
    def __init__(self, language: str = "english", strength: int = 256):
        self.language = language
        self.strength = strength

    async def generate_all_wallets(self, u_id: str, passphrase: str | None = None):
        session_connect = await AlchemyMaster.create_session()
        async with session_connect() as session:
            wallets = dict()
            tron_wallet = await self._generate_address(TronMainnet, passphrase=passphrase)
            tron_mnemomic = tron_wallet.get("mnemonic")
            eth_wallet = await self._generate_address(EthereumMainnet, passphrase=passphrase)
            eth_mnemomic = eth_wallet.get("mnemonic")
            bitcoin_wallet = await self._generate_address(BitcoinMainnet, passphrase=passphrase)
            bitcoin_mnemomic = bitcoin_wallet.get("mnemonic")

            new_wallets = dict()

            owner: Owner = await session.get(Owner, u_id)
            tronaddress: Address = Address(address=tron_wallet.get("address_0").get("address"),
                                           private_key=tron_wallet.get("address_0").get("private_key"))
            tronwallet = Wallet(blockchain="tron", mnemonic=tron_mnemomic)
            tronwallet.addresses.update({tron_wallet.get("address_0").get("address"): tronaddress})
            new_wallets["tron"] = tronwallet

            ethaddress: Address = Address(address=eth_wallet.get("address_0").get("address"),
                                          private_key=eth_wallet.get("address_0").get("private_key"))
            ethnwallet = Wallet(blockchain="ethereum", mnemonic=eth_mnemomic)
            ethnwallet.addresses.update({eth_wallet.get("address_0").get("address"): ethaddress})
            new_wallets["ethereum"] = ethnwallet

            bitaddress: Address = Address(address=bitcoin_wallet.get("address_0").get("address"),
                                          private_key=bitcoin_wallet.get("address_0").get("private_key"))
            bitwallet = Wallet(blockchain="bitcoin", mnemonic=bitcoin_mnemomic)
            bitwallet.addresses.update({bitcoin_wallet.get("address_0").get("address"): bitaddress})
            new_wallets["bitcoin"] = bitwallet

            owner.wallets.update(new_wallets)

            session.add(owner)
            await session.commit()
            try:
                wallets['tron'] = list(owner.wallets.get("tron").addresses.keys())[0]
                wallets['eth'] = list(owner.wallets.get("ethereum").addresses.keys())[0]
                wallets['bitcoin'] = list(owner.wallets.get("bitcoin").addresses.keys())[0]
            except Exception as e:
                print("Кошельки не создались", e)
            return new_wallets

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