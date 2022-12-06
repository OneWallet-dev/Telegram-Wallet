from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from Bot.handlers.Transaction_metods.transfer_hand import start_transfer
from Bot.keyboards.transaction_keys import m_transaction
from Bot.states.trans_states import TransactionStates, Trs_transfer
from Bot.utilts.mmanager import MManager

router = Router()
router.message.filter(StateFilter(TransactionStates))


@MManager.garbage_manage()
async def transaction_start(message: Message, state: FSMContext):
    # await message.delete() TODO понять что это и какое сообщение должно удаляться?
    grab = await message.answer('Данное меню предназначено для управления вашими активами',
                                reply_markup=m_transaction())
    await MManager.garbage_store(state, grab.message_id)


# @router.message(F.text == "⬅️ Назад")
# async def back(message: Message, state: FSMContext, bot: Bot):
#     await main_menu(message, state, bot)


@router.message(F.text == "🔄 Обменять")
async def trs_exchange(message: Message, state: FSMContext, bot: Bot, session: AsyncSession):
    await message.delete()
    await message.answer("Данное меню находится в разработке")


@router.message(F.text == "⤴️ Перевести")
async def trs_transfer(message: Message, state: FSMContext, bot: Bot):
    await message.delete()
    await state.set_state(Trs_transfer.new_transfer)
    await start_transfer(message, state, bot)


@router.message(F.text == "📝 История")
async def trs_history(message: Message, state: FSMContext, bot: Bot, session: AsyncSession):
    await message.delete()
    await message.answer("Данное меню находится в разработке")
