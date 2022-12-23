from aiogram.types import KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def main_menu_kb():
    mark = ReplyKeyboardBuilder()
    mark.row((KeyboardButton(text="Кошелек")))
    mark.add((KeyboardButton(text="AML")))
    mark.row((KeyboardButton(text="P2P")))
    mark.row((KeyboardButton(text="Настройки")))
    mark.row((KeyboardButton(text="Информация")))
    mark.adjust(2, 1, 2)
    return mark.as_markup(resize_keyboard=True)


def confirmation_button():
    mark = InlineKeyboardBuilder()
    mark.row((InlineKeyboardButton(text=f"Подтвердить", callback_data="confirm_thing")))
    return mark.as_markup(resize_keyboard=True)


def back_button():
    mark = InlineKeyboardBuilder()
    mark.row((InlineKeyboardButton(text=f"<< Назад", callback_data="back")))
    return mark.as_markup(resize_keyboard=True)


def auth_kb():
    mark = InlineKeyboardBuilder()
    mark.row((InlineKeyboardButton(text=f"➡️ Войти", callback_data="enter")))
    mark.row((InlineKeyboardButton(text=f"📝 Зарегистрироваться", callback_data="registration_init")))
    return mark.as_markup(resize_keyboard=True)
