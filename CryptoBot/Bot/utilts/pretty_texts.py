from Dao.DB_Redis import DataRedis
from Dao.models.Address import Address
from Services.EntServices.AddressService import AddressService
from Services.EntServices.OwnerService import OwnerService
from Services.EntServices.TokenService import TokenService


async def all_wallets_text(user_id: int):
    u_id = await DataRedis.find_user(user_id)
    user_tokens = await OwnerService.get_tokens(u_id)
    text = f'UID: <code>{u_id}</code> 👤\n'
    text += f'<b>Кошелек:</b>\n\n'
    if user_tokens:
        user_wallets = await OwnerService.get_wallets(u_id)
        text = f'<b>Кошелек пользователя <code>{u_id}</code></b>\n'
        text += '<b>Балансы:\n</b>'
        text += "<code>——————————————————————</code>\n"
        fee = 0
        for blockchain in user_wallets:
            addressess = user_wallets[blockchain].addresses
            for address in addressess:
                adress_obj = addressess.get(address)
                balances = await AddressService.get_balances(address=address)
                for token in adress_obj.tokens:
                    balance = balances.get(token.token_name, 'Iternal Error!')
                    text += f"{token.token_name}: {balance}\n"
                fee += adress_obj.get_address_freezed_fee()

        text += "<code>——————————————————————</code>\n"
        if fee:
            text += f'За пользование сервисом была заморожена комиссия: {fee} USDT\n'
        else:
            text += '<i>▫️ Для получения публичного адреса и списка транзакций нажмите ' \
                    '"Детальная информация о токене"</i>'
    else:
        text += '<i>▫️ Вы пока не отслеживаете ни один токен.</i>'
    return text


async def detail_view_text(user_id: int, token_name: str, token_network: str):
    u_id = await DataRedis.find_user(user_id)
    token_and_address = await TokenService.find_address_token(token_name=token_name,
                                                              token_network=token_network,
                                                              u_id=u_id)
    token = token_and_address.token
    address: Address = token_and_address.address

    balance = (await AddressService.get_balances(address=address.address, specific=[token]))[token.token_name]
    transactions = [str(address.transactions[transaction]) for transaction in address.transactions]

    text = f"<b>Токен: {token.token_name}\nСеть: {token.network}\nТекущий баланс: {balance}</b>\n\n"
    text += f"<b>Публичный адрес:</b> <code>{address.address}</code>\n"
    text += f"<i>- - Используйте его для получения транзакций - -</i>\n\n"
    text += f"<b>Список последних транзакций:</b>\n"
    if transactions:
        count = 0
        for trsc in transactions:
            if count < 3:
                text += f"<code>\n{trsc}\n</code>"
    else:
        text += f"<i>- - Список пока пуст - -</i>"
    return text, address.address
