from Bot.utilts.currency_helper import base_tokens
from Dao.models.Address import Address
from Dao.models.Wallet import Wallet


def pretty_wallet_text(user_wallets: dict[str: Wallet], user_balances: dict = None):
    text = 'Ваш кошелек содержит:\n\n'
    for blockchain in user_wallets:
        text += f"<b>{blockchain}</b>\n"
        basecoin = "BASECOIN"
        counter = 0
        for address in user_wallets[blockchain].addresses:
            text += "Адреса:\n"
            text += f"{counter}. <code>{address}</code>\n"
            # Использование user_balances
            text += f"{basecoin}: BASE COIN BALANCE"
            counter += 1
            for token in user_wallets[blockchain].addresses[address].tokens:
                # Использование user_balances
                balance = "BALANCE" if True else 0
                text += f"{token.token_name}: {balance}"
            text += "\n<code>——————————————————————</code>\n"
    return text
