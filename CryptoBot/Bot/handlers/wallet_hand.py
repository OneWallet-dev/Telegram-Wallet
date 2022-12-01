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
    confirm_delete_kb, delete_token_kb
from Bot.states.main_states import MainState
from Bot.states.wallet_states import WalletStates
from Bot.utilts.currency_helper import base_tokens
from Bot.utilts.mmanager import MManager
from Bot.utilts.pretty_texts import all_wallets_text
from Dao.models.Address import Address
from Dao.models.Owner import Owner
from Dao.models.Token import Token
from Services.address_service import AdressService
from Services.owner_service import OwnerService
from Services.token_service import TokenService
from crypto.TRON_wallet import Tron_wallet
from crypto.address_gen import Wallet_web3

router = Router()
router.message.filter(StateFilter(MainState.welcome_state, WalletStates))


@router.callback_query(F.data == 'refresh_wallet')
async def my_wallet_start(event: Message | CallbackQuery, state: FSMContext, bot: Bot, session: AsyncSession):
    message = event if isinstance(event, Message) else event.message
    user_id = event.from_user.id

    owner: Owner = await session.get(Owner, str(user_id))
    base_wallets = {"tron", "ethereum", "bitcoin"}
    if not {"tron", "ethereum", "bitcoin"}.issubset(set(owner.wallets)):
        if base_wallets.intersection(set(owner.wallets)):
            warning(f"The user {owner.id} {owner.username} does not have all wallets!")
            text = 'Похоже, что у вас присутствуют не все базовые кошельки. Пожалуйста, обратитесь в поддержку.'
        else:
            generator = Wallet_web3()
            owner_wallets = await generator.generate_all_walllets(user_id)
            await loader(message.chat.id, text="<i>Происходит генерация ваших основных кошельков.\n"
                                               "Пожалуйста, подождите.</i>")
    else:
        pass
    text = await all_wallets_text(user_id)

    keep_old = False if isinstance(event, Message) else True
    await MManager.sticker_surf(state=state, bot=bot, chat_id=message.chat.id, new_text=text,
                                keyboard=main_wallet_keys(), keep_old=keep_old)


@router.callback_query(F.data.startswith('refresh_wallet'))
async def wallet_refresh(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    await state.set_state(WalletStates.main)
    text = await all_wallets_text(callback.from_user.id)
    if 'edit' in callback.data:
        with suppress(TelegramBadRequest):
            await bot.edit_message_text(text=text, chat_id=callback.message.chat.id,
                                        message_id=callback.message.message_id, reply_markup=main_wallet_keys())
    elif 'keep' in callback.data:
        await callback.message.answer(text, reply_markup=main_wallet_keys())


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
            await OwnerService.add_currency(user=callback.from_user, token=token, network=network)
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


@router.callback_query(F.data == "delete_token", StateFilter(WalletStates.main))
async def delete_token(callback: CallbackQuery, state: FSMContext, bot: Bot, session: AsyncSession):
    await callback.answer()
    await state.set_state(WalletStates.delete_token)
    all_tokens = await OwnerService.get_tokens(callback.from_user.id)
    all_tokens_names = [f'{token.token_name} [{token.network}]' for token in all_tokens]
    await bot.edit_message_text('Выберите токен, который вы хотите удалить:',
                                chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                reply_markup=delete_token_kb(all_tokens_names))


@router.callback_query(F.data.startswith("del_t"), StateFilter(WalletStates.delete_token))
async def delete_token_conf(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    token, network = callback.data.replace('del_t_', "").replace('[', "").replace(']', "").split(" ")
    bal_data = await TokenService.balance_data(user_id=callback.from_user.id, token_name=token, token_network=network)
    address: str = bal_data['address']
    token_obj: Token = bal_data['token']
    balance = await AdressService.get_balances(address=address, specific=[token_obj])
    if balance:
        text = f"Обнаружены средства: {balance} {token_obj.token_name}\n" \
               f"Если вы удалите токен, они никуда не пропадут, " \
               f"но вы не сможете их отслеживать, пока не добавите его снова."
    else:
        text = "Средств не обнаружено, запись токена может быть безопасно удалена."
    await state.update_data(contract_Id=token_obj.contract_Id, address=address)
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
    for token in address_obj.tokens:
        if token.contract_Id == contract_id:
            address_obj.tokens.remove(token)
    session.add(address_obj)
    await session.commit()
