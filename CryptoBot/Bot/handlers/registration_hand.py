import re

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from Bot.handlers.m_menu_hand import main_menu
from Bot.keyboards.main_keys import confirmation_button, back_button
from Bot.states.main_states import RegistrationState
from Bot.utilts.mmanager import MManager
from Dao.DB_Redis import DataRedis
from Dao.models.Owner import Owner

router = Router()
router.message.filter(StateFilter(RegistrationState))


@router.callback_query(F.data == "registration_init")
@MManager.garbage_manage()
async def registration_start(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    await state.set_state(RegistrationState.main)
    msg_garb = await bot.edit_message_text(text="Здравствуйте.\n"
                                           "Для использования бота вам нужно установить сильный пароль.\n\n"
                                           "Обратите внимание, что все пароли хранятся в зашифрованном виде, и "
                                           "в случае утери восстановить аккаунт будет затруднительно.\n\n"
                                           "Для продолжения отправьте выбранный вами пароль:",
                                      chat_id=callback.message.chat.id,
                                      message_id=callback.message.message_id,
                                      reply_markup=back_button())
    msg_stick = await callback.message.answer("Для продолжения пришлите пароль:")
    await MManager.sticker_store(state, msg_stick)
    await MManager.garbage_store(state, msg_garb.message_id)
    await state.update_data(edit_msg=msg_stick.message_id)


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
    # session.add(Owner(id=str(callback.from_user.id), username=callback.from_user.username ))
    await session.commit()
    await session.close()
    u_id = await Owner.register(password=password)
    await callback.answer("Пароль успешно установлен")
    await DataRedis.authorize(callback.from_user.id, u_id)
    await MManager.clean(state, bot, callback.message.chat.id)
    await callback.message.answer(f'Вам присвоен уникальный ID: <code> {u_id} </code>\n'
                                  f'Запомните, а лучше запишите его: '
                                  f'вход в аккаунт производится <u>только</u> с помощью него.')
    await main_menu(callback, state, bot)
