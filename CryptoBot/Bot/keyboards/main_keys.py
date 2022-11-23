from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def start_kb():
    mark = ReplyKeyboardBuilder()
    mark.row((KeyboardButton(text="💹 Кошельки")))
    mark.row((KeyboardButton(text="✅ AML Check")))
    mark.row((KeyboardButton(text="💬 Поддержка")))
    return mark.as_markup(resize_keyboard=True)
