from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from Bot.keyboards.transaction_keys import m_transaction, trans_token_kb, trans_network_kb, change_transfer_token
from Bot.states.trans_states import Trs_transfer

router = Router()
router.message.filter(StateFilter(Trs_transfer))


@router.callback_query(lambda call: "transferToken_" in call.data, StateFilter(Trs_transfer.new_transfer))
async def start_transfer(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await callback.message.delete()
    await state.set_state(Trs_transfer.set_network)
    data = callback.data.split('_')
    token = data[-1]
    await state.update_data(token=token)
    text = "Перевод: token\nБаланс: Не определен\nСеть: Не выбрана\n" \
           "Адрес получателя: Не известен\n\n"
    text = text.replace("token", token)
    await state.update_data(text=text)
    network = ["TRC-20"]
    text = text + "В какой сети вы хотите перевести токен?"
    message = await callback.message.answer(text, reply_markup=trans_network_kb(network))
    await state.update_data(message_id=message.message_id)


@router.callback_query(lambda call: "transferNetwork_" in call.data, StateFilter(Trs_transfer.set_network))
async def start_transfer(callback: CallbackQuery, bot: Bot, state: FSMContext):
    sdata = await state.get_data()
    cdata = callback.data.split('_')
    network = cdata[-1]
    text = sdata.get("text")
    text = text.replace("Не выбрана", network)
    text = text.replace("Не определен", "1.0000")
    message_id = sdata.get("message_id")
    await state.update_data(network=network)
    text = text + "Напишите адрес получателя"
    await state.set_state(Trs_transfer.address)
    await bot.edit_message_text(text, callback.from_user.id, message_id, reply_markup=change_transfer_token())

@router.message(StateFilter(Trs_transfer.address))




