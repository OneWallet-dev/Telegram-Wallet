from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from Bot.keyboards.wallet_keys import AML_menu
from Bot.states.main_states import MainState

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