import re
from tkinter import Image

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove, InputFile, BufferedInputFile, InputMedia
from sqlalchemy.ext.asyncio import AsyncSession

from Bot.filters.wallet_filters import ChainOwned
from Bot.handlers.loading_handler import loader
from Bot.handlers.m_menu_hand import main_menu
from Bot.keyboards.main_keys import confirmation_button
from Bot.keyboards.wallet_keys import create_wallet_kb, currency_kb, use_wallet_kb, send_money_kb, send_money_confirm_kb
from Bot.states.main_states import MainState, RegistrationState
from Bot.states.wallet_states import WalletStates, WalletSendMoney
from Bot.utilts.mmanager import MManager
from Bot.utilts.currency_helper import base_tokens
from Bot.utilts.pretty_texts import pretty_balance
from Bot.utilts.qr_code_generator import qr_code
from Databases.DB_Postgres.models import Owner, Wallet
from cryptography.hazmat.primitives import hashes

router = Router()
router.message.filter(StateFilter(RegistrationState))


@MManager.garbage_manage()
async def registration_start(message: Message, state: FSMContext):
    await state.set_state(RegistrationState.main)
    msg_garb = await message.answer("Здравствуйте.\nДля использования бота вам нужно установить сильный пароль.\n\n"
                               "Обратите внимание, что все пароли хранятся в зашифрованном виде, и в случае утери "
                               "восстановить аккаунт будет затруднительно.\n\n")
    msg_stick = await message.answer("Для продолжения пришлите пароль:")
    await MManager.sticker_store(state, msg_stick)
    await MManager.garbage_store(state, msg_garb.message_id)


@router.message(StateFilter(RegistrationState.main, RegistrationState.check))
@MManager.garbage_manage()
async def password_confirmation(message: Message, bot: Bot, state: FSMContext):
    await bot.delete_message(message.chat.id, message.message_id)
    await state.set_state(RegistrationState.check)
    await state.update_data(password=message.text)
    text = await MManager.sticker_text(state)
    password_string = f"<code>{message.text}</code>"
    if "Для продолжения пришлите пароль:" in text:
        text = text.replace("Для продолжения пришлите пароль:", f"Выбранный вами пароль: {password_string}")
    else:
        text = re.sub(r"(?<=Выбранный вами пароль:).*", password_string, text)
    text += f"\n\nЕсли все верно, подтвердите его, нажав на кнопку под этим сообщением." \
            f"Если вы хотите выбрать другой пароль, то просто пришлите новое сообщение.\n\n" \
            f"ВНИМАНИЕ: ПОСЛЕ ПОДТВЕРЖДЕНИЯ ВСЕ СООБЩЕНИЯ, СОДЕРЖАЩИЕ ПАРОЛЬ, БУДУТ УДАЛЕНЫ!"
    await MManager.sticker_surf(state=state, bot=bot, chat_id=message.chat.id, new_text=text,
                                keyboard=confirmation_button())


@router.callback_query(F.data == "confirm_thing", StateFilter(RegistrationState.check))
@MManager.garbage_manage(clean=True)
async def registration(callback: CallbackQuery, state: FSMContext, session: AsyncSession, bot: Bot):
    password = (await state.get_data()).get("password")
    session.add(Owner(id=callback.from_user.id,username=callback.from_user.username, password = password))
    # await Owner.register(session, callback.from_user, password=password)
    await callback.answer("Пароль успешно установлен")
    await MManager.clean(state, bot, callback.message.chat.id)
    await main_menu(callback, state, bot)