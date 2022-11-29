from aiogram.types import InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from Bot.utilts.currency_helper import base_tokens


def m_transaction():
    mark = ReplyKeyboardBuilder()
    mark.row((KeyboardButton(text="Обменять")))
    mark.row((KeyboardButton(text="Перевести")))
    mark.row((KeyboardButton(text="Вывести")))
    mark.row((KeyboardButton(text="История")))
    mark.adjust(2)
    return mark.as_markup(resize_keyboard=True)


def trans_token_kb(custom_token_list: list | None = None):
    mark = InlineKeyboardBuilder()
    t_list = custom_token_list if custom_token_list else base_tokens.keys()
    for token in t_list:
        mark.row((InlineKeyboardButton(text=f"{token}", callback_data=f"transfer_{token}")))
    mark.adjust(2)
    return mark.as_markup(resize_keyboard=True)


def trans_network_kb(token: str, custom_network_list: list | None = None):
    mark = InlineKeyboardBuilder()
    n_list = custom_network_list if custom_network_list else base_tokens.get(token).get("networks").get("main")
    for network in n_list:
        mark.row((InlineKeyboardButton(text=f"{network} ({n_list[network]})", callback_data=f"new_n_{network}")))
    mark.adjust(2)
    return mark.as_markup(resize_keyboard=True)
