from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import hlink
from sqlalchemy.ext.asyncio import AsyncSession

from Bot.keyboards.transaction_keys import trans_network_kb, change_transfer_token, \
    kb_confirm_transfer, trans_token_kb, m_transaction
from Bot.states.trans_states import Trs_transfer, TransactionStates
from Bot.states.wallet_states import WalletStates
from Bot.utilts.currency_helper import blockchains, base_tokens
from Bot.utilts.fee_strategy import getFeeStrategy
from Bot.utilts.settings import DEBUG_MODE
from Dao.DB_Redis import DataRedis
from Dao.models.Address import Address
from Dao.models.Owner import Owner
from Dao.models.Token import Token
from Dao.models.Transaction import Transaction

from Services.EntServices.AddressService import AddressService
from Services.EntServices.TokenService import TokenService
from Services.EntServices.OwnerService import OwnerService

router = Router()
router.message.filter(StateFilter(Trs_transfer))

token_list = ["USDT"]
network_list = ["TRC-20"]


@router.callback_query(F.data == "send", StateFilter(WalletStates))
async def start_transfer(message: Message, state: FSMContext, bot: Bot):
    await state.set_state(Trs_transfer.new_transfer)
    await bot.send_message(message.from_user.id, "Выберите токен, который вы хотите перевести",
                           reply_markup=trans_token_kb(list(base_tokens.keys())))


@router.callback_query(lambda call: "transferToken_" in call.data, StateFilter(Trs_transfer.new_transfer))
async def token(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()

    c_data = callback.data.split('_')

    token_name = c_data[-1]

    text = "Перевод: token\nБаланс: Не определен\nСеть: Не выбрана\n" \
           "Адрес получателя: Не известен\nСумма: 0\nКомиссия: Не известна"
    text = text.replace("token", token_name)

    await state.update_data(text=text)
    await state.update_data(token_name=token_name)
    await state.set_state(Trs_transfer.set_network)

    text = text + "\n\n\n\n<b>В какой сети вы хотите перевести токен?</b>"

    message = await callback.message.answer(text, reply_markup=trans_network_kb(base_tokens[token_name]['network']))
    await state.update_data(message_id=message.message_id)


@router.callback_query(lambda call: "transferNetwork_" in call.data, StateFilter(Trs_transfer.set_network))
async def network(callback: CallbackQuery, bot: Bot, state: FSMContext):
    c_data = callback.data.split('_')
    s_data = await state.get_data()

    network = c_data[-1]
    token_name = s_data.get("token_name")
    text = s_data.get("text")
    message_id = s_data.get("message_id")

    token_obj = None
    blockchain = None

    if network in blockchains.get("tron").get("networks") or token_name == "TRX":
        token_obj = await TokenService.get_token(token_name, network)
        blockchain = "tron"
    elif network in blockchains.get("ethereum").get("networks"):
        blockchain = "ethereum"
    elif network in blockchains.get("bitcoin").get("networks"):
        blockchain = "bitcoin"

    # TODO ПРОВЕРКА АДРЕСА
    u_id = await DataRedis.find_user(int(callback.from_user.id))
    chain_address = await OwnerService().get_chain_address(u_id, blockchain)

    fee = await getFeeStrategy(chain_address)
    frozen_fee = chain_address.get_address_freezed_fee(token_name)

    token = await TokenService.get_token(token_name, network)
    balance_info = await AddressService().get_balances(chain_address.address, [token])
    token_balance = balance_info.get(token_name, 0.0)

    await state.update_data(contract_Id=token_obj.contract_Id)
    await state.update_data(u_address=chain_address.address)
    await state.update_data(network=network)
    await state.update_data(balance=token_balance)
    await state.update_data(frozen_fee=frozen_fee)
    await state.update_data(fee=fee)
    await state.update_data(blockchain=blockchain)

    text = text.replace("Не выбрана", network)
    text = text.replace("Не определен", str(token_balance))
    text = text.replace("Не известна", str(fee))

    await state.update_data(text=text)

    text = text + "\n\n\n\n<b>Напишите адрес получателя</b>>️\n" \
                  "Будьте очень внимательны и не торопитесь❗"

    await state.set_state(Trs_transfer.address)
    await bot.edit_message_text(text,
                                callback.from_user.id,
                                message_id,
                                reply_markup=change_transfer_token(),
                                parse_mode="HTML")


@router.message(StateFilter(Trs_transfer.address))
async def to_address(message: Message, state: FSMContext, bot: Bot):
    s_data = await state.get_data()
    text = s_data.get("text")
    token_name = s_data.get("token_name")
    message_id = s_data.get("message_id")
    to_address = message.text

    text = text.replace("Не известен", to_address)
    text = text + f"\n\n\n\n<b>Напишите сумму для перевода в {token_name}</b>❗️❗️\n"

    await state.update_data(to_address=to_address)

    await state.set_state(Trs_transfer.confirm_transfer)
    await bot.edit_message_text(text, message.from_user.id, message_id, reply_markup=change_transfer_token(),
                                parse_mode="HTML")


@router.message(StateFilter(Trs_transfer.confirm_transfer))
async def amount(message: Message, state: FSMContext, session: AsyncSession):
    await message.delete()
    try:
        amount = float(message.text)
    except Exception:
        await state.set_state(Trs_transfer.confirm_transfer)
        await message.answer("Вы указали неверное значение, пожалуйста укажите сумму для перевода в виде числа")
        return

    s_data = await state.get_data()

    token_name = s_data.get("token_name")
    network = s_data.get("network")
    to_address = s_data.get("to_address")
    blockchain = s_data.get("blockchain")
    balance = s_data.get("balance")
    frozen_fee = s_data.get("frozen_fee")
    fee = s_data.get("fee")

    if balance - frozen_fee < amount + fee:
        missing = float(amount + fee) - float(balance)
        await state.set_state(Trs_transfer.confirm_transfer)
        await message.answer(f"Для перевода вам не хватает: {missing} {token_name}\n\n"
                             f"Пожалуйста укажите другую сумму или пополните баланс\n\n"
                             f"Ваш баланс: {balance - frozen_fee} {token_name}\n"
                             f"Комиссия: {fee} {token_name}")
        return

    await state.update_data(amount=amount)
    await state.update_data(frozen_fee=frozen_fee)
    await state.update_data(fee=fee)

    text = f"Внимание! Вы совершаете транзакцию!\n________________________\n" \
           f"Перевод: {token_name}\nСеть: {network}\nАдрес получателя: {to_address}\n" \
           f"_________________________\nКомиссия: {fee} {token_name}\nСумма: {amount} {token_name}\n\n\n\n✅✅✅"
    await state.set_state(Trs_transfer.transfer)
    await message.answer(text, reply_markup=kb_confirm_transfer())


@router.callback_query(lambda call: "confirm_transfer_token" in call.data, StateFilter(Trs_transfer.transfer))
async def confirm(callback: CallbackQuery, bot: Bot, state: FSMContext, session: AsyncSession):
    await callback.message.delete()

    message = await bot.send_message(chat_id=callback.from_user.id, text="Устанавливается связь с блокчейном...")

    s_data = await state.get_data()
    token_name = s_data.get("token_name")
    contract_Id = s_data.get("contract_Id")
    network = s_data.get("network")
    to_address = s_data.get("to_address")
    blockchain = s_data.get("blockchain")
    amount = s_data.get("amount")

    u_id = await DataRedis.find_user(int(callback.from_user.id))
    owner: Owner = await session.get(Owner, u_id)
    address: Address = AddressService.get_address_for_transaction(owner, blockchain, contract_Id)
    token = await TokenService.get_token(token_name, network)

    transaction: Transaction = await AddressService().createTransaction(address,
                                                                        amount,
                                                                        token,
                                                                        to_address,
                                                                        message,
                                                                        callback.from_user.id
                                                                        )
    if transaction.status == "SUCCESS":
        await state.set_state(TransactionStates.main)
        if DEBUG_MODE:
            link = "https://nile.tronscan.org/#/transaction/"
        else:
            link = "https://tronscan.org/#/transaction/"
        link = hlink('ссылке', link + transaction.tnx_id)
        await callback.message.answer(
            f"Транзакция завершена!\n\nПроверить статус транзакции вы можете по {link}", reply_markup=m_transaction())

    else:
        print(transaction.status)
        await message.answer("ОШИБКА ТРАНЗАКЦИИ", reply_markup=m_transaction())
        await callback.message.answer("Ошибка транзакции")
        await state.set_state(TransactionStates.main)


@router.callback_query(lambda call: "cancel_transfer_token" in call.data, StateFilter(Trs_transfer.transfer))
async def cancel(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TransactionStates.main)
    await callback.message.delete()
    await callback.message.answer("Ваша транзакция отменена", m_transaction())
