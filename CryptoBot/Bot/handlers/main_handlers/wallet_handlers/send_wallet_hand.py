from aiogram import F, Bot, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from Bot.keyboards.transaction_keys import trans_token_kb, trans_network_kb
from Bot.states.trans_states import Trs_transfer
from Bot.states.wallet_states import WalletStates
from Bot.utilts.currency_helper import base_tokens
from Bot.utilts.mmanager import MManager
from Dao.models.bot_models import ContentUnit

router = Router()


@router.callback_query(F.data == "send", StateFilter(WalletStates))
async def start_transfer(message: Message, state: FSMContext, bot: Bot):
    await state.set_state(Trs_transfer.new_transfer)
    content: ContentUnit = await ContentUnit(tag="repl_choose_currency").get()
    await MManager.content_surf(event=message, state=state, bot=bot, content_unit=content,
                                keyboard=trans_token_kb(list(base_tokens.keys())),
                                placeholder_text="Выберите валюту для отправки:")


@router.callback_query(F.data.startswith("tToken_"), StateFilter(Trs_transfer.new_transfer))
async def token(callback: CallbackQuery, state: FSMContext, bot: Bot):
    c_data = callback.data.split('_')
    token_name = c_data[-1]
    await state.update_data(token_name=token_name)
    await state.set_state(Trs_transfer.set_network)
    text = "<b>Выберите сеть:</b>"
    content: ContentUnit = await ContentUnit(tag="repl_choose_network").get()
    await MManager.content_surf(event=callback, state=state, bot=bot, content_unit=content,
                                keyboard=trans_network_kb(base_tokens[token_name]['network']),
                                placeholder_text=text)


@router.callback_query(F.data.startswith("tNetwork_"), StateFilter(Trs_transfer.set_network))
async def network(callback: CallbackQuery, bot: Bot, state: FSMContext):
    network = callback.data.split('_')[-1]
    data = await state.get_data()
    token_name = data.get("token_name")
    text = data.get("text")

    token_obj = None
    blockchain = None

    if network in blockchains.get("tron").get("networks") or token_name == "TRX":  # TODO DRY
        token_obj = await TokenService.get_token(token_name, network)
        blockchain = "tron"
    elif network in blockchains.get("ethereum").get("networks"):
        token_obj = await TokenService.get_token(token_name, network)
        blockchain = "ethereum"
    elif network in blockchains.get("bitcoin").get("networks"):
        token_obj = await TokenService.get_token(token_name, network)
        blockchain = "bitcoin"

    # TODO ПРОВЕРКА АДРЕСА
    u_id = await DataRedis.find_user(int(callback.from_user.id))
    chain_address = await OwnerService().get_chain_address(u_id, blockchain)

    fee = await getFeeStrategy(chain_address)
    frozen_fee = chain_address.get_address_freezed_fee(token_name)

    token = await TokenService.get_token(token_name, network)
    print("token", token)
    balance_info = await AddressService().get_address_balances(chain_address.address, [token])
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

    content: ContentUnit = await ContentUnit(tag="repl_choose_address").get()
    content.text.format(info_text=text)
    await MManager.content_surf(event=callback, state=state, bot=bot, content_unit=content,
                                keyboard=change_transfer_token(),
                                placeholder_text=text)