from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from Bot.keyboards.transaction_keys import m_transaction, trans_token_kb
from Bot.states.trans_states import Trs_transfer

router = Router()
router.message.filter(StateFilter(Trs_transfer))


@router.callback_query("transfer" in F.data)
async def start_transfer(callback: CallbackQuery, bot: Bot, state: FSMContext):
    print(callback)
    print("hello")