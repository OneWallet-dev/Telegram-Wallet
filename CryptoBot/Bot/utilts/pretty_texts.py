from Bot.utilts.currency_helper import base_tokens, blockchains
from Dao.models.Address import Address
from Dao.models.Wallet import Wallet


def pretty_wallet_text(user_wallets: dict[str: Wallet], user_balances: dict = None):
    text = 'Ваш кошелек содержит:\n\n'
    for blockchain in user_wallets:
        text += f"<b>{blockchain}</b>\n"
        basecoin = blockchains.get(blockchain, {}).get("base_coin", "")
        counter = 0
        addressess = user_wallets[blockchain].addresses
        for address in addressess:
            text += "Адреса:\n"
            text += f"{counter}.: <code>{address}</code>\n"
            # Использование user_balances
            text += f"{basecoin}: BASE COIN BALANCE"
            counter += 1
            adress_obj = addressess.get(address)
            print(adress_obj.__dict__)
            print(adress_obj.tokens)
            for token in user_wallets[blockchain].addresses[address].tokens:
                # Использование user_balances
                balance = "BALANCE" if True else 0
                text += f"{token.token_name}: {balance}"
            text += "\n<code>——————————————————————</code>\n"
    return text
