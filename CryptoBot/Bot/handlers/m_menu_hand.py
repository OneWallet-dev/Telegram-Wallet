from aiogram import Router, Bot, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from requests import HTTPError
from sqlalchemy.ext.asyncio import AsyncSession

from Bot.keyboards.main_keys import main_menu_kb
from Bot.keyboards.wallet_keys import main_wallet_keys
from Bot.states.main_states import MainState
from Bot.states.trans_states import TransState
from Bot.states.wallet_states import WalletStates
from Bot.utilts.mmanager import MManager
from Databases.DB_Postgres.models import Owner, Wallet

router = Router()
router.message.filter(~StateFilter(TransState))


async def main_menu(update: Message | CallbackQuery, state: FSMContext, bot: Bot):
    message = update if isinstance(update, Message) else update.message
    await state.clear()
    await state.set_state(MainState.welcome_state)
    bot_name = (await bot.get_me()).full_name
    await message.answer(f'Добро пожаловать в главное меню криптовалютного бота {bot_name}\n'
                         'Чем я могу вам помочь?', reply_markup=main_menu_kb())



@router.message(F.text == "💹 Мой кошелек")
async def my_wallet_start(message: Message, state: FSMContext):
    await state.set_state(WalletStates.choose_currency)
    stick_msg = await message.answer('Список всех доступных криптовалют с балансом,'
                                     ' если валют нет, то сообщение о том, что валют нет',
                                     reply_markup=main_wallet_keys())
    await MManager.sticker_store(state, stick_msg)


@router.message(F.text == "👁‍🗨 AML Check")
async def my_wallet_start(message: Message, bot: Bot, state: FSMContext):
    stick_msg = await message.answer('AML проверка',
                                     reply_markup=main_wallet_keys())


@router.message(F.text == "↔️ Транзакции")
async def my_wallet_start(message: Message, bot: Bot, state: FSMContext):
    stick_msg = await message.answer('Совершение и контроль транзакций',
                                     reply_markup=main_wallet_keys())


