from aiogram import Router, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import hlink
from sqlalchemy.ext.asyncio import AsyncSession

from Bot.handlers.transaction_hand import transaction_start
from Bot.keyboards.transaction_keys import trans_network_kb, change_transfer_token, \
    kb_confirm_transfer
from Bot.states.trans_states import Trs_transfer, TransactionStates
from Bot.utilts.currency_helper import base_tokens, blockchains
from Bot.utilts.fee_strategy import getFeeStrategy
from Bot.utilts.settings import DEBUG_MODE
from CryptoMakers.Tron.Tron_TRC10_Maker import Tron_TRC10_Maker
from Dao.DB_Redis import DataRedis
from Dao.models.Address import Address
from Dao.models.Owner import Owner
from Dao.models.Token import Token
from Dao.models.Transaction import Transaction
from Services.AddressService import AddressService
from Services.TokenService import TokenService
from Services.owner_service import OwnerService
from CryptoMakers.Tron.Tron_TRC20_Maker import Tron_TRC20_Maker

router = Router()
router.message.filter(StateFilter(Trs_transfer))
router.message.filter(StateFilter(Trs_transfer))
tron = Tron_TRC20_Maker()


@router.callback_query(lambda call: "transferToken_" in call.data, StateFilter(Trs_transfer.new_transfer))
async def start_transfer(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.set_state(Trs_transfer.set_network)
    data = callback.data.split('_')
    token = data[-1]
    await state.update_data(token=token)
    text = "Перевод: token\nБаланс: Не определен\nСеть: Не выбрана\n" \
           "Адрес получателя: Не известен\nСумма: 0\n\n\n\n\n\n\n"
    text = text.replace("token", token)
    await state.update_data(text=text)

    network = ["TRC-20"]
    text = text + "В какой сети вы хотите перевести токен?"
    message = await callback.message.answer(text, reply_markup=trans_network_kb(network))
    await state.update_data(message_id=message.message_id)


@router.callback_query(lambda call: "transferNetwork_" in call.data, StateFilter(Trs_transfer.set_network))
async def start_transfer(callback: CallbackQuery, bot: Bot, state: FSMContext):#TODO рефакторинг! В на уровне роутеров мы не вызываем мейкеры. Только сервисы
    sdata = await state.get_data()
    cdata = callback.data.split('_')
    token = sdata.get("token")
    network = cdata[-1]
    token_info = base_tokens.get(token, None)
    owner = OwnerService()

    if token_info is not None:  # TODO Это надо вешать на удобные функции и модели
        if DEBUG_MODE:
            contract_address = token_info.get("testnet_contract_address")
        else:
            contract_address = token_info.get("contract_address")
    else:
        contract_address = None
        # пользовательский контракт
        pass
    await state.update_data(contract_address=contract_address)
    u_id = await DataRedis.find_user(callback.from_user.id)
    print(u_id)
    tron_address = await owner.get_chain_address(u_id, 'tron')
    if token == "TRX":  # TODO Это надо вешать на удобные функции и модели
        balance = await Tron_TRC10_Maker().TRX_get_balance(tron_address.address)
        frozen_fee = tron_address.get_address_freezed_fee("TRX")
        balance = balance-frozen_fee
    elif network in blockchains.get("tron").get("networks"):
        balance = await Tron_TRC20_Maker().get_balance(contract_address, tron_address.address)
        frozen_fee = tron_address.get_address_freezed_fee("USDT")
        balance = balance - frozen_fee
    else:
        raise ValueError("Network not supported")

    text = sdata.get("text")
    text = text.replace("Не выбрана", network)
    text = text.replace("Не определен", str(balance))
    message_id = sdata.get("message_id")
    await state.update_data(network=network)
    await state.update_data(balance=balance)
    await state.update_data(text=text)
    text = text + "<b>Напишите адрес получателя</b>️\n" \
                  "Будьте очень внимательны и не торопитесь❗"
    await state.set_state(Trs_transfer.address)
    await bot.edit_message_text(text,
                                callback.from_user.id,
                                message_id,
                                reply_markup=change_transfer_token(),
                                parse_mode="HTML")


@router.message(StateFilter(Trs_transfer.address))
async def address123(message: Message, state: FSMContext, bot: Bot):
    sdata = await state.get_data()
    text = sdata.get("text")
    message_id = sdata.get("message_id")
    address = message.text
    token = sdata.get("token")
    text = text.replace("Не известен", address)
    text = text + f"<b>Напишите сумму для перевода в {token}</b>❗️❗️\n"
    await state.update_data(address=address)
    await state.set_state(Trs_transfer.confirm_transfer)
    await bot.edit_message_text(text, message.from_user.id, message_id, reply_markup=change_transfer_token(),parse_mode="HTML")


@router.message(StateFilter(Trs_transfer.confirm_transfer))
async def confirm_transfer(message: Message, state: FSMContext, session: AsyncSession):
    await message.delete()
    u_id = await DataRedis.find_user(int(message.from_user.id))
    owner: Owner = await session.get(Owner, u_id)
    data = await state.get_data()
    contract_id = data.get("contract_address")
    token_object: Token = await TokenService.get_token(contract_id)
    address = AddressService.get_address_for_transaction(owner,
                                                     "tron",#TODO здесь не доджно быть хардкода
                                                     token_object.contract_Id)
    sdata = await state.get_data()
    fee = await getFeeStrategy(address)
    frozen_fee = address.get_address_freezed_fee()
    amount = float(message.text)
    print(amount)
    balance = sdata.get("balance")
    token_string = sdata.get("token")

    if balance < amount + fee:
        lacks_fee = (amount + fee) - (balance-frozen_fee)
        await message.answer(f"Вашего баланса недостаточно для перевода данной суммы:\n\n"
                             f"Баланс: {balance-frozen_fee} {token_string}\n"
                             f"Комиссия сети: {fee} {token_string}\n\n"
                             f"Для перевода не хватает: {lacks_fee} {token_string}")
        await message.answer("Пожалуйста напишите новую сумму или пополните баланс")
    else:
        network = sdata.get("network")
        to_address = sdata.get("address")
        await state.update_data(amount=amount)
        await state.update_data(fee=fee)
        text = f"Внимание! Вы совершаете транзакцию!\n________________________\n" \
               f"Перевод: {token_string}\nСеть: {network}\nАдрес получателя: {to_address}\n" \
               f"_________________________\nКомиссия: {fee} {token_string}\nСумма: {amount} {token_string}\n\n\n\n✅✅✅"
        await state.set_state(Trs_transfer.transfer)
        await message.answer(text, reply_markup=kb_confirm_transfer())


@router.callback_query(lambda call: "confirm_transfer_token" in call.data, StateFilter(Trs_transfer.transfer))
async def start_transfer(callback: CallbackQuery, bot: Bot, state: FSMContext, session: AsyncSession):
    await callback.message.delete()
    message = await bot.send_message(chat_id=callback.from_user.id, text="Начинаем транзакцию...")
    # await loader(chat_id=callback.from_user.id, text="Пожалуйста дождитесь завершения, транзакция выполняется",
    #              time=20)
    u_id = await DataRedis.find_user(int(callback.from_user.id))
    owner: Owner = await session.get(Owner, u_id)

    sdata = await state.get_data()
    contract_address = sdata.get("contract_address")
    network = sdata.get("network")
    to_address = sdata.get("address")
    amount = sdata.get("amount")
    fee = sdata.get("fee")

    if network in blockchains.get("tron").get("networks"):
        # wallet_private_key = list(owner.wallets.get("tron").addresses.values())[0].private_key
        address: Address = AddressService.get_address_for_transaction(owner,
                                                                      "tron",
                                                                      contract_address)
        print(address)
        print(network)
        if network == "TRC-10":
            pass
        if network == "TRC-20":

            if address:
                token = await TokenService.get_token(contract_address)
                transaction: Transaction = await AddressService().createTransaction(address,
                                                                                    amount,
                                                                                    token,
                                                                                    to_address,
                                                                                    message,
                                                                                    callback.from_user.id
                                                                                    )

                if transaction == "Недостаточно средств":
                    await state.set_state(TransactionStates.main)
                    await callback.message.answer(
                        f"Недостаточно средств") #TODO сделать нормальный баланс с учётом комиссии
                elif transaction.status == "SUCCESS":
                    await state.set_state(TransactionStates.main)
                    if DEBUG_MODE:
                        link = "https://nile.tronscan.org/#/transaction/"
                    else:
                        link = "https://tronscan.org/#/transaction/"
                    link = hlink('ссылке', link + transaction.tnx_id)
                    await callback.message.answer(
                        f"Транзакция завершена!\n\nПроверить статус транзакции вы можете по {link}")
                    await transaction_start(callback.message, state)
                else:
                    print(transaction.status)
                    await transaction_start(callback.message, state)
                    await callback.message.answer("Ошибка транзакции")
                    await state.set_state(TransactionStates.main)


@router.callback_query(lambda call: "cancel_transfer_token" in call.data, StateFilter(Trs_transfer.transfer))
async def start_transfer(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await state.set_state(TransactionStates.main)
    await callback.message.delete()
    await callback.message.answer("Ваша транзакция отменена")
    await transaction_start(callback.message, state)
