import asyncio
from contextlib import suppress
from logging import warning, info

from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, BufferedInputFile
from sqlalchemy.ext.asyncio import AsyncSession

from AllLogs.bot_logger import main_logger
from Bot.exeptions.wallet_ex import DuplicateToken
from Bot.keyboards.wallet_keys import add_token_kb, network_kb, refresh_button, main_wallet_keys, \
    confirm_delete_kb, delete_token_kb, inspect_token_kb
from Bot.states.main_states import MainState
from Bot.states.wallet_states import WalletStates
from Bot.utilts.currency_helper import base_tokens
from Bot.utilts.mmanager import MManager
from Bot.utilts.pretty_texts import all_wallets_text, detail_view_text
from Bot.utilts.qr_code_generator import qr_code
from Dao.DB_Redis import DataRedis
from Dao.models.Address import Address
from Dao.models.Owner import Owner
from Dao.models.Token import Token
from Dao.models.bot_models import ContentUnit
from Services.EntServices.AddressService import AddressService
from Services.EntServices.OwnerService import OwnerService
from Services.EntServices.TokenService import TokenService
from Services.CryptoMakers.address_gen import Wallet_web3

router = Router()
router.message.filter(StateFilter(MainState.welcome_state, WalletStates))


@router.callback_query(F.data.startswith('refresh_wallet'))
async def my_wallet_start(event: Message | CallbackQuery, state: FSMContext, bot: Bot):
    user_id = event.from_user.id
    u_id = await DataRedis.find_user(user_id)
    w_text = await all_wallets_text(u_id)
    content: ContentUnit = await ContentUnit(tag="main_menu").get()
    content.text = content.text.format(wallet_text=w_text, UID=u_id)
    await MManager.content_surf(event=event, state=state, bot=bot, content_unit=content,
                                keyboard=main_wallet_keys(),
                                placeholder_text=f"Кошелек пользователя {u_id}")
    await state.set_state(WalletStates.main)


# @router.callback_query(F.data.startswith('refresh_wallet'))
# async def wallet_refresh(callback: CallbackQuery, state: FSMContext, bot: Bot):
#     await state.set_state(WalletStates.main)
#     text = await all_wallets_text(callback.from_user.id)
#     await DataRedis.cache_text(callback.from_user.id, text, 'wallet')
#     if 'edit' in callback.data:
#         with suppress(TelegramBadRequest):
#             await bot.edit_message_text(text=text, chat_id=callback.message.chat.id,
#                                         message_id=callback.message.message_id, reply_markup=main_wallet_keys())
#     elif 'keep' in callback.data:
#         await callback.message.answer(text, reply_markup=main_wallet_keys())
#         await bot.edit_message_reply_markup(callback.message.chat.id, callback.message.message_id)
#     await callback.answer()


@router.callback_query(F.data.startswith('back_to_wall'))
async def wallet_backing(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await MManager.clean(state, bot, callback.message.chat.id)
    await state.set_state(WalletStates.main)
    text = await DataRedis.get_cached_text(callback.from_user.id, 'wallet')
    if not text:
        text = await all_wallets_text(callback.from_user.id)
        await DataRedis.cache_text(callback.from_user.id, text, 'wallet')
    await bot.edit_message_text(text=text, chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id, reply_markup=main_wallet_keys())
    await callback.answer()


@router.callback_query(F.data == "back", StateFilter(WalletStates.add_token))
@router.callback_query(F.data == "add_token", StateFilter(WalletStates.main))
async def add_token(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    await state.set_state(WalletStates.add_token)
    await bot.edit_message_text('Выберите токен, который вы хотите добавить:',
                                chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                reply_markup=add_token_kb())


@router.callback_query(F.data.startswith("new_t"), StateFilter(WalletStates.add_token))
async def add_network(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    token = callback.data.replace('new_t_', "")
    text = f"Токен: <code>{token}</code>\n\n"
    text += 'Выберите сеть из доступных для выбранного вами токена:'
    await state.update_data(token=token)
    await bot.edit_message_text(text=text,
                                chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                reply_markup=network_kb(token=token))


@router.callback_query(F.data.startswith("new_n"), StateFilter(WalletStates.add_token))
async def complete_token(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    token_name = data.get('token')
    network = callback.data.replace("new_n_", "")

    base_text = f"Токен: <code>{token_name}</code>\n" \
                f"В сети:  <code>{network}</code>\n"
    if network in base_tokens.get(token_name).get("network"):
        try:
            u_id = await DataRedis.find_user(callback.from_user.id)
            address: Address = await OwnerService.get_chain_address(u_id=u_id,
                                                                    blockchain=base_tokens.get(
                                                                        token_name).get("blockchain"))
            token: Token = await TokenService.get_token(token_name, network)
            if not token:
                token = await TokenService.form_base_token(token_name)
            await AddressService.add_currency(address=address, token=token)
        except DuplicateToken:
            await callback.answer('❌')
            text = "❌  ❌  ❌\n" \
                   "Данный токен уже отслеживается на этом кошельке.\n\n" + base_text
        else:
            await callback.answer('✅')
            text = f"✅  ✅  ✅\n" \
                   f"<b>Упешно добавлен:</b>\n\n" + base_text + "Баланс: <code>ВЫДАТЬ БАЛАНС</code>"
    else:
        await callback.answer('❌')
        text = "К сожалению, добавить токен в этой сети не удалось. Попробуйте позже."
    await state.set_state(WalletStates.main)
    await bot.edit_message_text(text=text,
                                chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                reply_markup=refresh_button())


@router.callback_query(F.data == "back", StateFilter(WalletStates.delete_token))
@router.callback_query(F.data == "delete_token", StateFilter(WalletStates.main))
async def delete_token(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()

    u_id = await DataRedis.find_user(callback.from_user.id)
    user_tokens = await OwnerService.get_tokens(u_id)
    if user_tokens:
        await state.set_state(WalletStates.delete_token)
        all_tokens_names = [f'{token.token_name} [{token.network}]' for token in user_tokens]
        await bot.edit_message_text('Выберите токен, который вы хотите удалить:',
                                    chat_id=callback.message.chat.id,
                                    message_id=callback.message.message_id,
                                    reply_markup=delete_token_kb(all_tokens_names))
    else:
        msg = await callback.message.answer(
            text='На ваших адресах пока нет токенов!')
        await asyncio.sleep(3)
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=msg.message_id)


@router.callback_query(F.data.startswith("del_t"), StateFilter(WalletStates.delete_token))
async def delete_token_conf(callback: CallbackQuery, state: FSMContext, bot: Bot):
    token, network = callback.data.replace('del_t_', "").replace('[', "").replace(']', "").split(" ")
    u_id = await DataRedis.find_user(callback.from_user.id)
    bal_data = await TokenService.find_address_token(u_id, token_name=token, token_network=network)
    address = bal_data.address
    token_obj = bal_data.token
    balance = (await AddressService.get_balances(address=address.address, specific=[token_obj]))[token_obj.token_name]
    if balance > 0:
        text = f"Обнаружены средства: {token_obj.token_name}: {balance}\n" \
               f"Если вы удалите токен, они никуда не пропадут, " \
               f"но вы не сможете их отслеживать, пока не добавите его снова."
    else:
        text = "Средств не обнаружено, запись токена может быть безопасно удалена."
    await callback.answer()
    await state.update_data(contract_Id=token_obj.contract_Id, address=address.address, token_name=str(token_obj))
    await bot.edit_message_text(text=text, chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                reply_markup=confirm_delete_kb())


@router.callback_query(F.data.startswith("сonfirm_delete"), StateFilter(WalletStates.delete_token))
async def delete_confirm(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    contract_id = data.get('contract_Id')
    address = data.get('address')
    text = "Непредвиденная ошибка"
    try:
        await AddressService.remove_currency(address, contract_id)
    except Exception as ex:
        print(ex)
    else:
        text = f"Вы больше не отслеживаете токен {str(data.get('token_name'))}"
    await callback.answer()
    await bot.edit_message_text(text=text, chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                reply_markup=refresh_button())


@router.callback_query(F.data.startswith("inspect_token"), StateFilter(WalletStates.main))
async def inspect_token_start(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()

    u_id = await DataRedis.find_user(callback.from_user.id)
    user_tokens = await OwnerService.get_tokens(u_id)
    if user_tokens:
        await state.set_state(WalletStates.inspect_token)
        msg = await bot.edit_message_text("Выберите токен, который вы хотите изучить подробнее:",
                                          chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                          reply_markup=inspect_token_kb(user_tokens))
        await MManager.sticker_store(state, msg)
    else:
        msg = await callback.message.answer(
            text='На ваших адресах пока нет токенов!')
        await asyncio.sleep(3)
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=msg.message_id)


@router.callback_query(F.data.startswith("inspect_t_"), StateFilter(WalletStates.inspect_token))
async def inspect_one_token(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await MManager.clean(state, bot, chat_id=callback.message.chat.id)
    token, network = callback.data.replace('inspect_t_', "").replace('[', "").replace(']', "").split(" ")
    text, address = await detail_view_text(token_name=token, token_network=network, user_id=callback.from_user.id)

    qr = await qr_code(address)
    img = BufferedInputFile(file=qr, filename=str(address) + ".PNG")

    u_id = await DataRedis.find_user(callback.from_user.id)
    user_tokens = await OwnerService.get_tokens(u_id)
    with suppress(TelegramBadRequest):
        garb = await callback.message.answer_photo(photo=img)
        await MManager.sticker_surf(state, bot, callback.message.chat.id, text, inspect_token_kb(user_tokens))
        await MManager.garbage_store(state=state, tech_msg_id=garb.message_id)
    await callback.answer()


@router.callback_query(F.data == "put_money", StateFilter(WalletStates.inspect_token))
async def put_money(callback: CallbackQuery):
    await callback.message.answer("Функция пополнения кошелька фиатными валютами находится в разработке")
