from aiogram import F, Bot, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from Bot.keyboards.transaction_keys import trans_token_kb, trans_network_kb
from Bot.keyboards.wallet_keys import addresses_kb
from Bot.states.trans_states import Trs_transfer
from Bot.states.wallet_states import WalletStates
from Bot.utilts.ContentService import ContentService
from Bot.utilts.currency_helper import base_tokens
from Bot.utilts.fee_strategy import getFeeStrategy
from Bot.utilts.mmanager import MManager
from Bot.utilts.settings import DEBUG_MODE
from Dao.DB_Redis import DataRedis
from Dao.models.Token import Token
from Dao.models.bot_models import ContentUnit
from Services.EntServices.AddressService import AddressService
from Services.EntServices.OwnerService import OwnerService
from Services.EntServices.TokenService import TokenService

router = Router()


@router.callback_query(F.data == "send", StateFilter(WalletStates))
async def start_transfer(message: Message, state: FSMContext, bot: Bot):
    await state.set_state(Trs_transfer.new_transfer)
    content: ContentUnit = await ContentUnit(tag="repl_choose_currency").get()
    all_tokens_list = await TokenService.all_tokens()
    await MManager.content_surf(event=message, state=state, bot=bot, content_unit=content,
                                keyboard=trans_token_kb(all_tokens_list),
                                placeholder_text="Выберите валюту для отправки:")


@router.callback_query(F.data.startswith("tToken_"), StateFilter(Trs_transfer.new_transfer))
async def token(callback: CallbackQuery, state: FSMContext, bot: Bot):
    c_data = callback.data.split('_')
    token_name = c_data[-1]
    await state.update_data(token_name=token_name)
    await state.set_state(Trs_transfer.set_network)
    text = "<b>Выберите сеть:</b>"
    content: ContentUnit = await ContentUnit(tag="repl_choose_network").get()
    algos = await TokenService.alorithms_for_token_name(token_name=token_name)
    await MManager.content_surf(event=callback, state=state, bot=bot, content_unit=content,
                                keyboard=trans_network_kb(algos),
                                placeholder_text=text)


@router.callback_query(F.data.startswith("tAlgos_"), StateFilter(Trs_transfer.set_network))
async def algorithm_use(callback: CallbackQuery, bot: Bot, state: FSMContext):
    algo = callback.data.split('_')[-1]
    data = await state.get_data()
    token_name = data.get("token_name")
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

    fee = await getFeeStrategy(chain_address)
    frozen_fee = chain_address.get_address_freezed_fee(token_name)
    balance_info = await AddressService().get_address_balances(chain_address.address, [token])
    token_balance = balance_info.get(token_name, 0.0)

    await state.update_data(contract_Id=token_obj.contract_Id)
    await state.update_data(u_address=chain_address.address)
    await state.update_data(alorithm=algo)
    await state.update_data(balance=token_balance)
    await state.update_data(frozen_fee=frozen_fee)
    await state.update_data(fee=fee)
    await state.update_data(blockchain=blockchain)

    placeholder_text = f"Выбранная валюта: {token_obj.token_name}\n" \
           f"Выбранная сеть: {token_obj.algorithm.name}\n" \
           "Минимальная сумма отправки: 3 USDT\n" \
           f"Комиссия: {fee} USDT"

    await state.set_state(Trs_transfer.address)

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
    await state.update_data(adresses=adresses_dict)

    placeholder_text = "Доступные адреса:\n\n" \
                f"{addresses_text}\n\n" \
                "Выберите адрес c которого хотите отправить"

    if content.text:
        content.text = content.text.format(addresses_text=addresses_text)

    await MManager.content_surf(event=callback.message, state=state, bot=bot, content_unit=content,
                                placeholder_text=placeholder_text, keyboard=addresses_kb(counter, new_button=False))
