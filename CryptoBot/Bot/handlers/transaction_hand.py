from aiogram import Router, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from Bot.states.trans_states import TransactionStates

router = Router()
router.message.filter(StateFilter(TransactionStates))


async def transaction_start(message: Message, bot: Bot, state: FSMContext):
    stick_msg = await message.answer('Совершение и контроль транзакций')
