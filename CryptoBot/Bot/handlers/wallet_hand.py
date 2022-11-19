from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from Bot.filters.wallet_filters import WalletExists
from Bot.keyboards.wallet_keys import currency_kb
from Bot.states.main_states import MainState
from Bot.states.wallet_states import WalletStates

router = Router()
router.message.filter(StateFilter(MainState.welcome_state, WalletStates))


@router.message(F.text == "💹 Кошелек", StateFilter(MainState.welcome_state))
async def choose_currency(message: Message, state: FSMContext):
    await state.set_state(WalletStates.choose_currency)
    await message.answer('Выберите валюту', reply_markup=currency_kb())


@router.message(WalletExists(), StateFilter(WalletStates.choose_currency))
async def choose_currency(message: Message, state: FSMContext):
    await state.set_state(WalletStates.choose_currency)
    await message.answer('Выберите валюту', reply_markup=currency_kb())
