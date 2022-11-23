from aiogram.types import KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from Bot.keyboards.base_keys import back_button
from Bot.utilts.currency_helper import currencies


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
    mark.row((KeyboardButton(text=f"🪙 Получить деньги 🪙")))
    mark.row((KeyboardButton(text=f"🪙 Отправить деньги 🪙")))

    return mark.as_markup(resize_keyboard=True)
