from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def currency_kb():
    mark = ReplyKeyboardBuilder()
    imitate_currency_list = ["USDT (TRC-20)"]
    for currency in imitate_currency_list:
        mark.row((KeyboardButton(text=currency)))
    return mark.as_markup(resize_keyboard=True)
