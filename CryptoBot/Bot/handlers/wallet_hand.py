from tkinter import Image

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove, InputFile, BufferedInputFile, InputMedia
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from Bot.exeptions.wallet_ex import DuplicateToken
from Bot.filters.wallet_filters import ChainOwned
from Bot.handlers.loading_handler import loader
from Bot.handlers.m_menu_hand import my_wallet_start
from Bot.keyboards.wallet_keys import create_wallet_kb, currency_kb, use_wallet_kb, send_money_kb, \
    send_money_confirm_kb, token_kb, network_kb, refresh_button
from Bot.states.main_states import MainState
from Bot.states.wallet_states import WalletStates, WalletSendMoney
from Bot.utilts.mmanager import MManager
from Bot.utilts.currency_helper import base_tokens
from Bot.utilts.pretty_texts import pretty_balance
from Bot.utilts.qr_code_generator import qr_code
from Dao.models.Owner import Owner
from Dao.models.Wallet import Wallet

router = Router()
router.message.filter(StateFilter(MainState.welcome_state, WalletStates, WalletSendMoney))


@router.callback_query(F.data == "add_token", StateFilter(WalletStates.create_token))
async def add_token(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    await bot.edit_message_text('Выберите токен, который вы хотите добавить:',
                                chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                reply_markup=token_kb())


@router.callback_query(F.data.startswith("new_t"), StateFilter(WalletStates.create_token))
async def add_network(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    token = callback.data.replace('new_t_', "")
    text = f"Токен: <code>{token}</code>\n\n"
    text += 'Выберите сеть из доступных для выбранного вами токена:'
    await state.update_data(token=token)
    await bot.edit_message_text(text=text,
                                chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                reply_markup=network_kb(token=token))


@router.callback_query(F.data.startswith("new_n"), StateFilter(WalletStates.create_token))
async def complete_token(callback: CallbackQuery, state: FSMContext, bot: Bot, session: AsyncSession):
    data = await state.get_data()
    token = data.get('token')
    network = callback.data.replace("new_n_", "")

    base_text = f"Токен: <code>{token}</code>\n" \
                f"В сети:  <code>{network}</code>\n"
    if network in base_tokens.get(token).get("network"):
        try:
            await Owner.add_currency(user=callback.from_user, token=token, network=network)
        except DuplicateToken:
            await callback.answer('❌')
            text = "❌  ❌  ❌\n" \
                   "Данный токен уже отслеживается на этом кошельке.\n\n" + base_text
        else:
            await callback.answer('✅')
            text = f"✅  ✅  ✅\n" \
                   f"<b>Упешно добавлен:</b>\n\n" + base_text + "Баланс: <code>ВЫДАТЬ БАЛАНС</code>"
    else:
        await callback.answer('❌')
        text = "К сожалению, добавить токен в этой сети не удалось. Попробуйте позже."
    await bot.edit_message_text(text=text,
                                chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                reply_markup=refresh_button())
