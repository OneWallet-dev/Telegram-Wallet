from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession

from Bot.handlers.loading_handler import loader
from Bot.keyboards.wallet_keys import create_wallet_kb, currency_kb, use_wallet_kb, send_money_kb, \
    send_money_confirm_kb, AML_menu
from Bot.states.main_states import MainState
from Bot.states.wallet_states import WalletStates
from Bot.utilts.mmanager import MManager
from Bot.utilts.currency_helper import base_tokens
from Bot.utilts.pretty_texts import pretty_balance
from Databases.DB_Postgres.models import Owner, Wallet

router = Router()
router.message.filter(StateFilter(MainState.welcome_state, MainState.AML_check))


@router.message(F.text == "✅ AML Check", StateFilter(MainState.welcome_state))
async def AML_hello(message: Message, state: FSMContext):
    await state.set_state(MainState.AML_check)
    await message.answer('Отправьте мне адрес вашего кошелька, чтобы проверить'
                         ' причастность криптовалюты к незаконной деятельности',
                         reply_markup=AML_menu())


@router.message(StateFilter(MainState.AML_check))
async def AML_hello(message: Message, state: FSMContext):
    await message.answer('Ваш адрес:',
                         reply_markup=AML_menu())