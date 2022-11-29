from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import hlink
from sqlalchemy.ext.asyncio import AsyncSession

from Bot.handlers.transaction_hand import transaction_start
from Bot.keyboards.transaction_keys import m_transaction, trans_token_kb, trans_network_kb, change_transfer_token, \
    kb_confirm_transfer
from Bot.states.trans_states import Trs_transfer, TransactionStates
from Bot.utilts.currency_helper import base_tokens
from Dao.models.Owner import Owner
from crypto.TRON_wallet import Tron_wallet

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
           "Адрес получателя: Не известен\nСумма: 0\n\n"
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
async def address(message: Message, state: FSMContext, bot: Bot, session: AsyncSession):
    sdata = await state.get_data()
    text = sdata.get("text")
    message_id = sdata.get("message_id")

    address = message.text
    token = sdata.get("token")
    text = text.replace("Не известен", address)
    text = text + f"Напишите сумму для перевода в {token}"
    await state.update_data(address=address)
    await state.set_state(Trs_transfer.confirm_transfer)
    await bot.edit_message_text(text, message.from_user.id, message_id, reply_markup=change_transfer_token())

@router.message(StateFilter(Trs_transfer.confirm_transfer))
async def confirm_transfer(message: Message, state: FSMContext, bot: Bot, session: AsyncSession):
    await message.delete()
    sdata = await state.get_data()
    message_id = sdata.get("message_id")

    token = sdata.get("token")
    network = sdata.get("network")
    to_address = sdata.get("address")
    amount = float(message.text)
    fee = 1.0
    res_sum = amount + fee
    await state.update_data(amount=amount)
    await state.update_data(fee=fee)
    text = f"Внимание! Вы совершаете транзакцию!\n________________________\n" \
           f"Перевод: {token}\nСеть: {network}\nАдрес получателя: {to_address}\n" \
           f"_________________________\nКомиссия: {fee} {token}\nСумма: {res_sum} {token}"
    await state.set_state(Trs_transfer.transfer)
    await message.answer(text, reply_markup=kb_confirm_transfer())


@router.callback_query(lambda call: "confirm_transfer_token" in call.data, StateFilter(Trs_transfer.transfer))
async def start_transfer(callback: CallbackQuery, bot: Bot, state: FSMContext, session: AsyncSession):
    owner: Owner = await session.get(Owner, str(callback.from_user.id))
    network_dict = {"tron": ["TRC-20", "TRC-10"], 'ethereum': ["ERC-20"], 'bitcoin': ["bitcoin"]}

    sdata = await state.get_data()
    token = sdata.get("token")
    network = sdata.get("network")
    to_address = sdata.get("address")
    amount = sdata.get("amount")
    fee = sdata.get("fee")

    token_info = base_tokens.get(token, None)
    if token_info is not None:
        contract_address = token_info.get("contract_address")
    else:
        contract_address = None
        # пользовательский контракт
        pass
    if network in network_dict.get("tron"):
        tron = Tron_wallet('mainnet')
        wallet_private_key = list(owner.wallets.get("tron").addresses.values())[0].private_key
        wallet_address = list(owner.wallets.get("tron").addresses.values())[0].address
        if network == "TRC-10":
            pass
        else:

            th = await tron.trc20_transfer(wallet_private_key, contract_address, wallet_address, to_address, int(amount))
            if "https://tronscan.org/" in th:
                link = hlink('ссылке', th)
                await callback.message.delete()
                await callback.message.answer(f"Транзакция завершена!\n\nПроверить статус транзакции вы можете по {link}")
            else:
                await callback.answer("Ошибка транзакции, пожалуйста проверьте баланс")

    elif network in network_dict.get("ethereum"):
        wallet_private_key = list(owner.wallets.get("ethereum").addresses.values())[0].private_key
        wallet_address = list(owner.wallets.get("ethereum").addresses.values())[0].address


@router.callback_query(lambda call: "cancel_transfer_token" in call.data, StateFilter(Trs_transfer.transfer))
async def start_transfer(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await state.set_state(TransactionStates.main)
    await callback.message.delete()
    await callback.message.answer("Ваша транзакция отменена")
    await transaction_start(callback.message, bot, state)



