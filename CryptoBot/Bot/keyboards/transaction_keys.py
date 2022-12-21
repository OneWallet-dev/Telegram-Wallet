from aiogram.types import InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from Bot.keyboards.base_keys import rep_back_button
from Bot.utilts.currency_helper import base_tokens


def m_transaction():
    mark = ReplyKeyboardBuilder()
    mark.row((KeyboardButton(text="🔄 Обменять")))
    mark.row((KeyboardButton(text="⤴️ Перевести")))
    mark.row((KeyboardButton(text="📝 История")))
    mark.row((KeyboardButton(text="⬅️ Назад")))
    mark.adjust(2, 1, 1, 1)
    return mark.as_markup(resize_keyboard=True)


def trans_token_kb(custom_token_list: list | None = None):
    mark = InlineKeyboardBuilder()
    t_list = custom_token_list if custom_token_list else base_tokens.keys()
    for token in t_list:
        mark.row((InlineKeyboardButton(text=f"{token}", callback_data=f"tToken_{token}")))
    mark.adjust(2)
    return mark.as_markup(resize_keyboard=True)


def trans_network_kb(custom_network_list: list | None = None):
    mark = InlineKeyboardBuilder()
    for network in custom_network_list:
        mark.row((InlineKeyboardButton(text=f"{network}", callback_data=f"tNetwork_{network}")))
    mark.adjust(2)
    return mark.as_markup(resize_keyboard=True)


def change_transfer_token():
    mark = InlineKeyboardBuilder()
    mark.row((InlineKeyboardButton(text="Изменить токен", callback_data="change_transfer_token")))
    return mark.as_markup(resize_keyboard=True)


def kb_confirm_transfer():
    mark = InlineKeyboardBuilder()
    mark.row((InlineKeyboardButton(text="Подтвердить перевод", callback_data="confirm_transfer_token")))
    mark.row((InlineKeyboardButton(text="Отменить перевод", callback_data="cancel_transfer_token")))
    return mark.as_markup(resize_keyboard=True)

