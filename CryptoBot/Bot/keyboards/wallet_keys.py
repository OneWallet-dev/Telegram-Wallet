from aiogram.types import KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from Bot.keyboards.base_keys import back_button
from Bot.utilts.currency_helper import currencies


def main_wallet_keys():
    mark = InlineKeyboardBuilder()
    mark.row((InlineKeyboardButton(text=f"Добавить токен", callback_data="add_token")))
    mark.row((InlineKeyboardButton(text=f"Удалить токен", callback_data="delete_token")))
    mark.row((InlineKeyboardButton(text=f"Детальный вид", callback_data="inspect_token")))
    mark.adjust(2, 1)
    return mark.as_markup(resize_keyboard=True)


def token_kb(custom_token_list: list | None = None):
    mark = InlineKeyboardBuilder()
    t_list = custom_token_list if custom_token_list else currencies.keys()
    for token in t_list:
        mark.row((InlineKeyboardButton(text=f"{token}", callback_data=f"new_t_{token}")))
    mark.adjust(2)
    return mark.as_markup(resize_keyboard=True)


def network_kb(token: str, custom_network_list: list | None = None):
    mark = InlineKeyboardBuilder()
    n_list = custom_network_list if custom_network_list else currencies.get(token).get("networks").get("main")
    for network in n_list:
        mark.row((InlineKeyboardButton(text=f"{network} ({n_list[network]})", callback_data=f"new_n_{network}")))
    mark.adjust(2)
    return mark.as_markup(resize_keyboard=True)


def currency_kb():
    mark = InlineKeyboardBuilder()
    for currency in currencies:
        chain = currencies[currency]
        mark.row((InlineKeyboardButton(text=f"{currency} [{chain}]",
                                       callback_data=chain)))
    return mark.as_markup(resize_keyboard=True)


@back_button
def create_wallet_kb(blockchain_name: str):
    mark = ReplyKeyboardBuilder()
    mark.row((KeyboardButton(text=f"🪙 Открыть кошелек в сети {blockchain_name} 🪙")))
    return mark.as_markup(resize_keyboard=True)


@back_button
def use_wallet_kb():
    mark = ReplyKeyboardBuilder()
    mark.row((KeyboardButton(text=f"💸 Отправить деньги 💸")))
    return mark.as_markup(resize_keyboard=True)


@back_button
def AML_menu():
    mark = ReplyKeyboardBuilder()
    return mark.as_markup(resize_keyboard=True)


def send_money_kb(token_list: list[str]):
    mark = InlineKeyboardBuilder()
    for token in token_list:
        mark.row((InlineKeyboardButton(text=f"{token}", callback_data=token)))
    return mark.as_markup(resize_keyboard=True)


def send_money_confirm_kb(confirm_push: int):
    mark = InlineKeyboardBuilder()
    text = "Подтвердить"
    data = 'more_conf'
    if confirm_push == 1:
        data = 'send_confirmed'
        text += " 🟩"
    elif confirm_push == 2:
        text = "🟩 " + text + " 🟩"
    elif confirm_push == 3:
        text = "✅ ОПЕРАЦИЯ ПОДТВЕРЖДЕНА ✅"
        data = 'send_sucсess'
    elif confirm_push == 66:
        text = "❌ ОШИБКА В ОПЕРАЦИИ ❌"
        data = 'send_error'
    mark.row((InlineKeyboardButton(text=text, callback_data=data)))
    return mark.as_markup(resize_keyboard=True)
