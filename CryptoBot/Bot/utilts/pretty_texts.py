from aiogram.types import User

from Bot.utilts.currency_helper import base_tokens, blockchains
from Dao.models.Address import Address
from Dao.models.Wallet import Wallet
from Services.address_service import AdressService
from Services.owner_service import OwnerService
from Services.token_service import TokenService


async def all_wallets_text(user_id: int):
    user_wallets = await OwnerService.get_wallets(user_id)
    text = '<b>Кошелек пользователя UID</b>\n'
    text += '<b>Балансы:\n</b>'
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
    text += '<i>▫️ Для получения адреса нужного кошелька нажмите "Детальный вид"</i>'
    return text


async def detail_view_text(user_id: int, token_name: str, token_network: str):
    token_and_address = await TokenService.find_address_token(token_name=token_name,
                                                              token_network=token_network,
                                                              user_id=user_id)
    token = token_and_address.get('token')
    address = token_and_address.get('address')
    balance = (await AdressService.get_balances(address=address.address, specific=[token]))[token.token_name]
    transactions = [str(transaction) for transaction in address.transactions]

    text = f"<b>Токен: {token.token_name}\nСеть: {token.network}\nТекущий баланс: {balance}</b>\n\n"
    text += f"<b>Публичный адрес:</b> <code>{address.address}</code>\n"
    text += f"<i>- - Используйте его для получения транзакций - -</i>\n\n"
    text += f"<b>Список транзакций:</b>\n"
    if transactions:
        for trsc in transactions:
            text += f" - {trsc}"
    else:
        text += f"<i>- - Список пока пуст - -</i>"
    return text
