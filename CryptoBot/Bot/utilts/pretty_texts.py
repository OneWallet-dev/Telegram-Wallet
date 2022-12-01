from Bot.utilts.currency_helper import base_tokens, blockchains
from Dao.models.Address import Address
from Dao.models.Wallet import Wallet
from Services.address_service import AdressService
from Services.owner_service import OwnerService


async def all_wallets_text(user_id: int):
    user_wallets = await OwnerService.get_wallets(user_id)
    text = 'Ваш кошелек содержит:\n'
    text += "<code>——————————————————————</code>\n"
    for blockchain in user_wallets:
        addressess = user_wallets[blockchain].addresses
        for address in addressess:
            adress_obj = addressess.get(address)
            balances = await AdressService.get_balances(address=address)
            for token in adress_obj.tokens:
                balance = balances.get(token.token_name, 'Iternal Error!')
                text += f"{token.token_name}: {balance}\n"
    text += "<code>——————————————————————</code>\n"
    return text
