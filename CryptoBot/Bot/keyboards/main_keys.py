from aiogram.types import KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def main_menu_kb():
    mark = ReplyKeyboardBuilder()
    mark.row((KeyboardButton(text="👁‍🗨 AML Check")))
    mark.row((KeyboardButton(text="↔️ Транзакции")))
    mark.row((KeyboardButton(text="💹 Мой кошелек")))
    mark.row((KeyboardButton(text="💬 Поддержка")))
    mark.adjust(2, 1, 1)
    return mark.as_markup(resize_keyboard=True)


def confirmation_button():
    mark = InlineKeyboardBuilder()
    mark.row((InlineKeyboardButton(text=f"Подтвердить", callback_data="confirm_thing")))
    return mark.as_markup(resize_keyboard=True)
