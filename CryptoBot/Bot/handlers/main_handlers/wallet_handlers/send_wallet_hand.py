from aiogram import F, Bot, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import hlink
from sqlalchemy.ext.asyncio import AsyncSession

from Bot.keyboards.main_keys import back_button
from Bot.keyboards.transaction_keys import trans_token_kb, trans_network_kb, kb_confirm_transfer, m_transaction
from Bot.keyboards.wallet_keys import addresses_kb
from Bot.states.trans_states import Trs_transfer, TransactionStates
from Bot.states.wallet_states import WalletStates
from Bot.utilts.ContentService import ContentService
from Bot.utilts.FunctionalService import perform_sending
from Bot.utilts.fee_strategy import getFeeStrategy
from Bot.utilts.mmanager import MManager
from Bot.utilts.settings import DEBUG_MODE
from Dao.DB_Redis import DataRedis
from Dao.models.Address import Address
from Dao.models.Owner import Owner
from Dao.models.Token import Token
from Dao.models.Transaction import Transaction
from Dao.models.bot_models import ContentUnit
from Services.EntServices.AddressService import AddressService
from Services.EntServices.OwnerService import OwnerService
from Services.EntServices.TokenService import TokenService

router = Router()


@router.callback_query(F.data == "back", StateFilter(Trs_transfer.set_network))
@router.callback_query(F.data == "send", StateFilter(WalletStates))
async def start_transfer(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(Trs_transfer.new_transfer)
    content: ContentUnit = await ContentUnit(tag="repl_choose_currency").get()
    all_tokens_list = await TokenService.all_tokens()
    await MManager.content_surf(event=callback, state=state, bot=bot, content_unit=content,
                                keyboard=trans_token_kb(all_tokens_list),
                                placeholder_text="Выберите валюту для отправки:")


@router.callback_query(F.data == "back", StateFilter(Trs_transfer.address))
@router.callback_query(F.data.startswith("tToken_"), StateFilter(Trs_transfer.new_transfer))
async def choose_network(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    if callback.data != 'back':
        token_name = callback.data.split('_')[-1]
    else:
        token_name = data.get('token_name')
    await state.update_data(token_name=token_name)
    await state.set_state(Trs_transfer.set_network)
    text = "<b>Выберите сеть:</b>"
    content: ContentUnit = await ContentUnit(tag="repl_choose_network").get()
    algos = await TokenService.alorithms_for_token_name(token_name=token_name)
    await MManager.content_surf(event=callback, state=state, bot=bot, content_unit=content,
                                keyboard=trans_network_kb(algos),
                                placeholder_text=text)


@router.callback_query(F.data == "back", StateFilter(Trs_transfer.confirm_transfer, Trs_transfer.amount))
@router.callback_query(F.data.startswith("tAlgos_"), StateFilter(Trs_transfer.set_network))
async def algorithm_use(callback: CallbackQuery, bot: Bot, state: FSMContext):
    data = await state.get_data()
    if callback.data != "back":
        algo = callback.data.split('_')[-1]
        print(1, algo)
    else:
        algo = data.get("algorithm")
        print(2, algo)
    token_name = data.get("token_name")
    print(token_name)
    text = data.get("text")

    main_net = not DEBUG_MODE
    token_obj: Token = await TokenService.get_token(token_name=token_name, token_algorithm=algo, main_net=main_net)

    if token_obj.algorithm.blockchain == token_obj.network.blockchain:
        blockchain = token_obj.algorithm.blockchain
    else:
        raise Exception("Bases are broken!")

    # TODO ПРОВЕРКА АДРЕСА

    u_id = await DataRedis.find_user(int(callback.from_user.id))
    chain_address = await OwnerService().get_chain_address(u_id, blockchain)

    fee = await getFeeStrategy(token_obj)
    print(fee)
    frozen_fee = chain_address.get_address_freezed_fee(token_name)
    balance_info = await AddressService().get_address_balances(chain_address.address, [token_obj])
    token_balance = balance_info.get(token_name, 0.0)

    await state.update_data(contract_Id=token_obj.contract_Id)
    await state.update_data(u_address=chain_address.address)
    await state.update_data(algorithm=algo)
    await state.update_data(balance=token_balance)
    await state.update_data(frozen_fee=frozen_fee)
    await state.update_data(fee=fee)
    await state.update_data(blockchain=blockchain)


    placeholder_text = f"Выбранная валюта: {token_obj.token_name}\n" \
           f"Выбранная сеть: {token_obj.algorithm.name}\n" \
           "Минимальная сумма отправки: 3 USDT\n" \
           f"Комиссия: {fee} USDT"


    content: ContentUnit = await ContentUnit(tag="repl_token_conditions").get()
    content.text.format(token=token_obj.token_name, network=token_obj.algorithm.name, fee=fee)
    msg = await ContentService.send(content=content, bot=bot,
                              chat_id=callback.message.chat.id,
                              placeholder_text=placeholder_text)
    await MManager.garbage_store(state, msg.message_id)

    addresses = await OwnerService.get_all_chain_addresses(u_id=u_id, blockchain=blockchain)
    content: ContentUnit = await ContentUnit(tag="addresses_for_transfer").get()

    counter = 1
    adresses_dict = dict()
    addresses_text = str()
    for address in addresses:
        addresses_text += f"{counter}. <code>{address}</code>\n"
        adresses_dict.update({counter: address})
        counter += 1
    await state.update_data(from_addresses=adresses_dict)

    placeholder_text = "Доступные адреса:\n\n" \
                f"{addresses_text}\n\n" \
                "Выберите адрес c которого хотите отправить"

    if content.text:
        content.text = content.text.format(addresses_text=addresses_text)

    await MManager.content_surf(event=callback.message, state=state, bot=bot, content_unit=content,
                                placeholder_text=placeholder_text, keyboard=addresses_kb(counter, new_button=False))
    await state.set_state(Trs_transfer.address)


@router.callback_query(StateFilter(Trs_transfer.address))
async def choosen_address(callback: CallbackQuery, bot: Bot, state: FSMContext, session: AsyncSession):
    address_nmbr = callback.data
    data = await state.get_data()
    from_addresses = data.get('from_addresses')
    algo = data.get("algorithm")
    token_name = data.get('token_name')

    address: Address = await session.get(Address, from_addresses.get(address_nmbr))

    main_net = not DEBUG_MODE
    token_obj: Token = await TokenService.get_token(token_name=token_name, token_algorithm=algo, main_net=main_net)
    balance = await AddressService.get_address_balances(address=address.address, specific=[token_obj])
    await state.update_data(address=address.address)

    content: ContentUnit = await ContentUnit(tag="transfer_choose_address").get()
    info_text = f"Выбранный адрес:\n\n<code>{address.address}</code>\nБаланс:{balance[token_name]}\n" \
                f"Выберите сумму которую хотите отправить:"
    if content.text:
        content.text = content.text.format(info_text=info_text)
    await MManager.content_surf(event=callback, state=state, bot=bot, content_unit=content,
                                placeholder_text=info_text)
    await state.set_state(Trs_transfer.amount)


@router.message(StateFilter(Trs_transfer.amount))
async def choose_amount(message: Message, bot: Bot, state: FSMContext, session: AsyncSession):
    if not message.text.replace(".", "", 1).isdigit():
        await message.answer("Вы указали неверное значение, пожалуйста укажите сумму для перевода в виде числа")
        return
    else:
        amount = float(message.text)

    s_data = await state.get_data()
    token_name = s_data.get("token_name")
    balance = s_data.get("balance")
    frozen_fee = s_data.get("frozen_fee")
    fee = s_data.get("fee")

    if balance - frozen_fee < amount + fee:
        missing = float(amount + fee) - float(balance)
        text = f"Для перевода вам не хватает: {missing} {token_name}\n\n" \
               f"Пожалуйста укажите другую сумму или пополните баланс\n\n" \
               f"Ваш баланс: {balance - frozen_fee} {token_name}\n" \
               f"Комиссия: {fee} {token_name}"
        keyboard = back_button()
    else:
        await state.set_state(Trs_transfer.choose_where)
        text = f"Введите адрес на который хотите отправить USDT в сети TRC-20 или UID пользователя"
        keyboard = None

    await state.update_data(amount=amount)

    content: ContentUnit = await ContentUnit(tag="send_approve_transfer").get()
    content.text.format(info_text=text)
    await MManager.content_surf(event=message, state=state, bot=bot, content_unit=content, placeholder_text=text,
                                keyboard=keyboard)


@router.message(StateFilter(Trs_transfer.choose_where))
async def transfer_info(message: Message, bot: Bot, state: FSMContext):
    to_address = message.text
    s_data = await state.get_data()
    token_name = s_data.get("token_name")
    algorithm_name = s_data.get("algorithm")
    amount = s_data.get("amount")
    from_address = s_data.get("address")
    fee = s_data.get("fee")
    info_text = f"Выбранная валюта: {token_name}\n" \
                f"Выбранная сеть: {algorithm_name}\n" \
                f"Кошелек отправки: {from_address}\n" \
                f"Кошелек получения: {to_address}\n" \
                f"Сумма перевода: {amount} {token_name}\n" \
                f"Комиссия: {fee}\n" \
                f"Сумма к получению: {amount - fee}"

    content: ContentUnit = await ContentUnit(tag="send_choose_where").get()
    print(1)
    print(1)
    print(algorithm_name)
    print(1)
    await state.update_data(algorithm_name=algorithm_name)
    await state.update_data(to_address=to_address)
    await state.set_state(Trs_transfer.confirm_transfer)
    content.text.format(info_text=info_text)
    await MManager.content_surf(event=message, state=state, bot=bot, content_unit=content, placeholder_text=info_text,
                                keyboard=kb_confirm_transfer())


@router.callback_query(lambda call: "confirm_transfer_token" in call.data, StateFilter(Trs_transfer.confirm_transfer))
async def confirm(callback: CallbackQuery, bot: Bot, state: FSMContext, session: AsyncSession):
    message = await bot.send_message(chat_id=callback.from_user.id, text="Устанавливается связь с блокчейном...")
    s_data = await state.get_data()
    token_name = s_data.get("token_name")
    contract_Id = s_data.get("contract_Id")
    algorithm_name = s_data.get("algorithm_name")
    to_address = s_data.get("to_address")
    blockchain = s_data.get("blockchain")
    amount = s_data.get("amount")
    print(token_name)
    print(contract_Id)
    print(algorithm_name)
    print(to_address)
    print(blockchain)
    print(amount)

    u_id = await DataRedis.find_user(int(callback.from_user.id))

    owner: Owner = await session.get(Owner, u_id)
    address: Address = AddressService.get_address_for_transaction(owner, blockchain, contract_Id)

    main_net = not DEBUG_MODE
    token = await TokenService.get_token(token_name=token_name, token_algorithm=algorithm_name, main_net=main_net)
    if not token:
        raise Exception(f"TOKEN {token_name} {algorithm_name} {'MAINNET' if main_net else 'TESTNET'} NOT FOUND IN GIVEN ")

    transaction: Transaction = await perform_sending(address, amount, token, to_address, message, callback.from_user.id)

    if transaction.status == "SUCCESS":
        if DEBUG_MODE:
            link = "https://nile.tronscan.org/#/transaction/"
        else:
            link = "https://tronscan.org/#/transaction/"
        link = hlink('ссылке', link + transaction.tnx_id)
        text = f"Транзакция завершена!\n\nПроверить статус транзакции вы можете по {link}"
    else:
        print(transaction.status)
        text = "ОШИБКА ТРАНЗАКЦИИ"
    await state.set_state(TransactionStates.main)

    content: ContentUnit = await ContentUnit(tag="send_trans_result").get()
    content.text.format(info_text=text)
    await MManager.content_surf(event=message, state=state, bot=bot, content_unit=content,
                                keyboard=m_transaction(),
                                placeholder_text=text)
