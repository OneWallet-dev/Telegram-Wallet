from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from Bot.utilts.currency_helper import base_tokens


def trans_token_kb(custom_token_list: list | None = None):
    mark = InlineKeyboardBuilder()
    t_list = custom_token_list if custom_token_list else base_tokens.keys()
    for token in t_list:
        mark.row((InlineKeyboardButton(text=f"{token}", callback_data=f"new_t_{token}")))
    mark.adjust(2)
    return mark.as_markup(resize_keyboard=True)


def trans_network_kb(token: str, custom_network_list: list | None = None):
    mark = InlineKeyboardBuilder()
    n_list = custom_network_list if custom_network_list else base_tokens.get(token).get("networks").get("main")
    for network in n_list:
        mark.row((InlineKeyboardButton(text=f"{network} ({n_list[network]})", callback_data=f"new_n_{network}")))
    mark.adjust(2)
    return mark.as_markup(resize_keyboard=True)
