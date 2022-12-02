import asyncio
from contextlib import suppress
from logging import warning

from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from Bot.handlers.loading_handler import loader
from Bot.exeptions.wallet_ex import DuplicateToken
from Bot.keyboards.wallet_keys import add_token_kb, network_kb, refresh_button, main_wallet_keys, \
    confirm_delete_kb, delete_token_kb, inspect_token_kb
from Bot.states.main_states import MainState
from Bot.states.wallet_states import WalletStates
from Bot.utilts.currency_helper import base_tokens
from Bot.utilts.mmanager import MManager
from Bot.utilts.pretty_texts import all_wallets_text, detail_view_text
from Dao.DB_Redis import DataRedis
from Dao.models.Address import Address
from Dao.models.Owner import Owner
from Dao.models.Token import Token
from Services.AddressService import AddressService
from Services.owner_service import OwnerService
from Services.TokenService import TokenService
from crypto.address_gen import Wallet_web3

router = Router()
router.message.filter(StateFilter(MainState.welcome_state, WalletStates))


async def my_wallet_start(event: Message | CallbackQuery, state: FSMContext, bot: Bot, session: AsyncSession):
    message = event if isinstance(event, Message) else event.message
    user_id = event.from_user.id

    u_id = await DataRedis.find_user(message.from_user.id)
    owner: Owner = await session.get(Owner, u_id)
    base_wallets = {"tron", "ethereum", "bitcoin"}
    if not {"tron", "ethereum", "bitcoin"}.issubset(set(owner.wallets)):
        if base_wallets.intersection(set(owner.wallets)):
            warning(f"The user {owner.id} {owner.username} does not have all wallets!")
            text = 'Похоже, что у вас присутствуют не все базовые кошельки. Пожалуйста, обратитесь в поддержку.'
        else:
            generator = Wallet_web3()
            await generator.generate_all_wallets(u_id)
            await loader(message.chat.id, text="<i>Происходит генерация ваших основных кошельков.\n"
                                               "Пожалуйста, подождите.</i>")
    else:
        pass
    text = await all_wallets_text(user_id)

    state_str = await state.get_state()
    if 'MainState' not in state_str:
        await MManager.sticker_surf(state=state, bot=bot, chat_id=message.chat.id, new_text=text,
                                    keyboard=main_wallet_keys())
    else:
        msg = await message.answer(text, reply_markup=main_wallet_keys())
        await MManager.sticker_store(state, msg)
    await state.set_state(WalletStates.main)


@router.callback_query(F.data.startswith('refresh_wallet'))
async def wallet_refresh(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(WalletStates.main)
    text = await all_wallets_text(callback.from_user.id)
    await DataRedis.cache_text(callback.from_user.id, text, 'wallet')
    if 'edit' in callback.data:
        with suppress(TelegramBadRequest):
            await bot.edit_message_text(text=text, chat_id=callback.message.chat.id,
                                        message_id=callback.message.message_id, reply_markup=main_wallet_keys())
    elif 'keep' in callback.data:
        await callback.message.answer(text, reply_markup=main_wallet_keys())
        await bot.edit_message_reply_markup(callback.message.chat.id, callback.message.message_id)
    await callback.answer()


@router.callback_query(F.data.startswith('back_to_wall'))
async def wallet_backing(callback: CallbackQuery, state: FSMContext, bot: Bot):
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
async def complete_token(callback: CallbackQuery, state: FSMContext, bot: Bot, session: AsyncSession):
    data = await state.get_data()
    token = data.get('token')
    network = callback.data.replace("new_n_", "")

    base_text = f"Токен: <code>{token}</code>\n" \
                f"В сети:  <code>{network}</code>\n"
    if network in base_tokens.get(token).get("network"):
        try:
            u_id = await DataRedis.find_user(callback.from_user.id)
            await OwnerService.add_currency(u_id, token=token, network=network)
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
async def delete_token(callback: CallbackQuery, state: FSMContext, bot: Bot, session: AsyncSession):
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
    await callback.answer()
    token, network = callback.data.replace('del_t_', "").replace('[', "").replace(']', "").split(" ")
    u_id = await DataRedis.find_user(callback.from_user.id)
    bal_data = await TokenService.find_address_token(u_id, token_name=token, token_network=network)
    address: Address = bal_data.get('address')
    token_obj: Token = bal_data.get('token')
    balance = (await AddressService.get_balances(address=address.address, specific=[token_obj]))[token_obj.token_name]
    if balance > 0:
        text = f"Обнаружены средства: {token_obj.token_name}: {balance}\n" \
               f"Если вы удалите токен, они никуда не пропадут, " \
               f"но вы не сможете их отслеживать, пока не добавите его снова."
    else:
        text = "Средств не обнаружено, запись токена может быть безопасно удалена."
    await state.update_data(contract_Id=token_obj.contract_Id, address=address.address)
    await bot.edit_message_text(text=text, chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                reply_markup=confirm_delete_kb())


@router.callback_query(F.data.startswith("сonfirm_delete"), StateFilter(WalletStates.delete_token))
async def delete_confirm(callback: CallbackQuery, state: FSMContext, bot: Bot, session: AsyncSession):
    await callback.answer()
    data = await state.get_data()
    contract_id = data.get('contract_Id')
    address = data.get('address')
    address_obj: Address = await session.get(Address, address)
    text = "Непредвиденная ошибка"
    for token in address_obj.tokens:
        if token.contract_Id == contract_id:
            address_obj.tokens.remove(token)
            session.add(address_obj)
            await session.commit()
            text = f"Вы больше не отслеживаете токен {str(token)}"
            break
        text = f"Произошла ошибка: токен с заданным контрактом не был обнаружен на данном адресе."
    await bot.edit_message_text(text=text, chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                reply_markup=refresh_button())


@router.callback_query(F.data.startswith("inspect_token"), StateFilter(WalletStates.main))
async def inspect_token_start(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()

    u_id = await DataRedis.find_user(callback.from_user.id)
    user_tokens = await OwnerService.get_tokens(u_id)
    if user_tokens:
        await state.set_state(WalletStates.inspect_token)
        await bot.edit_message_text("Выберите токен, который вы хотите изучить подробнее:",
                                    chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                    reply_markup=inspect_token_kb(user_tokens))
    else:
        msg = await callback.message.answer(
            text='На ваших адресах пока нет токенов!')
        await asyncio.sleep(3)
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=msg.message_id)


@router.callback_query(F.data.startswith("inspect_t_"), StateFilter(WalletStates.inspect_token))
async def inspect_one_token(callback: CallbackQuery, bot: Bot):
    token, network = callback.data.replace('inspect_t_', "").replace('[', "").replace(']', "").split(" ")
    text = await detail_view_text(token_name=token, token_network=network, user_id=callback.from_user.id)
    u_id = await DataRedis.find_user(callback.from_user.id)
    user_tokens = await OwnerService.get_tokens(u_id)
    with suppress(TelegramBadRequest):
        await bot.edit_message_text(text, chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                    reply_markup=inspect_token_kb(user_tokens))
    await callback.answer()


@router.callback_query(F.data == "put_money", StateFilter(WalletStates.inspect_token))
async def put_money(callback: CallbackQuery):
    await callback.message.answer("Функция пополнения кошелька находится в разработке")
