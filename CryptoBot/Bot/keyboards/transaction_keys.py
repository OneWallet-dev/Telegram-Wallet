from aiogram.types import InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from Bot.keyboards.base_keys import rep_back_button
from Bot.utilts.currency_helper import base_tokens
from Dao.models import Algorithm
from Dao.models.Token import Token
from Services.EntServices.TokenService import TokenService


def m_transaction():
    mark = ReplyKeyboardBuilder()
    mark.row((KeyboardButton(text="🔄 Обменять")))
    mark.row((KeyboardButton(text="⤴️ Перевести")))
    mark.row((KeyboardButton(text="📝 История")))
    mark.row((KeyboardButton(text="⬅️ Назад")))
    mark.adjust(2, 1, 1, 1)
    return mark.as_markup(resize_keyboard=True)


def trans_token_kb(custom_token_list: list[Token]):
    mark = InlineKeyboardBuilder()
    token_names = [token.token_name for token in custom_token_list]
    for token_name in token_names:
        mark.row((InlineKeyboardButton(text=f"{token_name}", callback_data=f"tToken_{token_name}")))
    mark.adjust(2)
    return mark.as_markup(resize_keyboard=True)


def trans_network_kb(custom_network_list: list[Algorithm] | None = None):
    mark = InlineKeyboardBuilder()
    algo_names = [algo.name for algo in custom_network_list]
    for algo_name in algo_names:
        mark.row((InlineKeyboardButton(text=f"{algo_name}", callback_data=f"tAlgos_{algo_name}")))
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

