from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def main_kb():
    mark = ReplyKeyboardBuilder()
    mark.row((KeyboardButton(text="👁‍🗨BUTTON👁‍🗨")))
    return mark.as_markup(resize_keyboard=True)
