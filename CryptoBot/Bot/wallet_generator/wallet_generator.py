from bip_utils import Bip44Coins as COIN, Bip44, Bip39SeedGenerator, Bip44Changes

from Bot.wallet_generator.mnemonic import Mnemonic


class wallet_bip44(Mnemonic):
    def __init__(self, language: str = "english", strength: int = 128):
        super().__init__(language=language)
        self.mnemonic = self.generate_mnemo(strength=strength)

    async def create_TRON(self, amount_wallets: int = 1):

        seed_bytes = Bip39SeedGenerator(self.mnemonic).Generate()

        bip44_mst_ctx = Bip44.FromSeed(seed_bytes, COIN.TRON)

        bip44_acc_ctx = bip44_mst_ctx.Purpose().Coin().Account(0)

        bip44_chg_ctx = bip44_acc_ctx.Change(Bip44Changes.CHAIN_EXT)
        if amount_wallets >= 1:
            wallets = dict()
            for i in range(amount_wallets):
                bip44_addr_ctx = bip44_chg_ctx.AddressIndex(i)
                wallets[f"ADDRESS {i}"] = {
                    "PrivateKey": bip44_addr_ctx.PrivateKey().ToExtended(),
                    "PublicKey": bip44_addr_ctx.PublicKey().ToExtended(),
                    "Address": bip44_addr_ctx.PublicKey().ToAddress(),
                    "Mnemonic": self.mnemonic
                }
            return wallets
        else:
            raise ValueError("Please enter the correct wallet value")


