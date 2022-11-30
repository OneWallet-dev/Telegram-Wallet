from Bot.utilts.currency_helper import base_tokens, blockchains
from Dao.models.Address import Address
from Dao.models.Wallet import Wallet
from Services.owner_service import OwnerService
from crypto.TRON_wallet import Tron_wallet


async def all_wallets_text(user_id: int):
    user_wallets = await OwnerService.get_wallets(user_id)
    text = 'Ваш кошелек содержит:\n'
    text += "<code>——————————————————————</code>\n"
    for blockchain in user_wallets:
        # text += f"<b>{blockchain}</b>\n\n"
        # counter = 0
        addressess = user_wallets[blockchain].addresses
        for address in addressess:
            # text += "Адреса:\n"
            # text += f"{counter}.: <code>{address}</code>\n"
            # Использование user_balances
            # counter += 1
            adress_obj = addressess.get(address)
            for token in adress_obj.tokens:
                balance = await Tron_wallet().get_balance(contract=token.contract_Id, address=address)
                balance = balance if isinstance(balance, int) else balance["Error"]
                text += f"{token.token_name}: {balance}\n"
    text += "<code>——————————————————————</code>\n"
    return text
