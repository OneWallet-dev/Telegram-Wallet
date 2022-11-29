from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from Bot.keyboards.transaction_keys import m_transaction, trans_token_kb
from Bot.states.trans_states import TransactionStates, Trs_transfer

router = Router()
router.message.filter(StateFilter(TransactionStates))


async def transaction_start(message: Message, bot: Bot, state: FSMContext):
    stick_msg = await message.answer('Данное меню предназначено для управления вашими активами',
                                     reply_markup=m_transaction())



@router.message(F.text == "Обменять")
async def trs_exchange(message: Message, state: FSMContext, bot: Bot, session: AsyncSession):
    pass

@router.message(F.text == "Перевести")
async def trs_transfer(message: Message, state: FSMContext, bot: Bot, session: AsyncSession):
    print(1)
    await state.set_state(Trs_transfer.new_transfer)
    token_list = ["USDT"]
    await message.answer("Выберите токен, который вы хотите перевести", reply_markup=trans_token_kb(token_list))

@router.message(F.text == "Вывести")
async def trs_withdrawal(message: Message, state: FSMContext, bot: Bot, session: AsyncSession):
    pass

@router.message(F.text == "История")
async def trs_history(message: Message, state: FSMContext, bot: Bot, session: AsyncSession):
    pass
