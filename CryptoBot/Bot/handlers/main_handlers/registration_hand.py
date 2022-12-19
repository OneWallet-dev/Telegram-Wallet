import re

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from AllLogs.bot_logger import main_logger
from Bot.handlers.main_handlers.main_menu_hand import main_menu, title_entry_point
from Bot.keyboards.main_keys import confirmation_button, back_button
from Bot.states.main_states import RegistrationState
from Bot.utilts.mmanager import MManager
from Dao.DB_Redis import DataRedis
from Dao.models.Owner import Owner
from Services.CryptoMakers.address_gen import Wallet_web3
from Services.EntServices.OwnerService import OwnerService

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
    password_string = f" <tg-spoiler>{message.text}</tg-spoiler>"
    keyboard = None

    if "Для продолжения пришлите пароль:" in text:
        text = text.replace("Для продолжения пришлите пароль:", f"Выбранный вами пароль: {password_string}\n"
                                                                f"Введите его еще раз:")
    elif re.search(fr"(?<=<tg-spoiler>)({message.text})(?=</tg-spoiler>)", text):
        text = text.replace("Введите его еще раз:", "\nТеперь подтвердите пароль, нажав на кнопку.\n\n"
                                                    "<b>ВНИМАНИЕ! ЭТО УДАЛИТ ВСЕ СООБЩЕНИЯ, СОДЕРЖАЩИЕ ПАРОЛЬ</b>")
        keyboard = confirmation_button()
    else:
        text = re.sub(r"(?<=Выбранный вами пароль:).*", password_string, text)
        if "еще раз" not in text:
            text += f"\n\nВведите его еще раз:"

    await MManager.sticker_surf(state=state, bot=bot, chat_id=message.chat.id, new_text=text,
                                keyboard=keyboard)


@router.callback_query(F.data == "confirm_thing", StateFilter(RegistrationState.check))
@MManager.garbage_manage(clean=True)
async def registration(callback: CallbackQuery, state: FSMContext, bot: Bot):
    password = (await state.get_data()).get("password")
    u_id = await OwnerService.register(password=password)
    main_logger.infolog.info(f"New user {u_id} [{callback.from_user.id} {callback.from_user.username}]")

    generator = Wallet_web3()
    await generator.generate_all_wallets(u_id)
    main_logger.infolog.info(f"Wallets generated for user {u_id}")

    await callback.answer("Пароль успешно установлен")
    await DataRedis.authorize(callback.from_user.id, u_id)
    await MManager.clean(state, bot, callback.message.chat.id)
    await callback.message.answer(f'Вам присвоен уникальный ID:<code> {u_id} </code>\n'
                                  f'Запомните, а лучше запишите его: '
                                  f'вход в аккаунт производится <u>только</u> с помощью него.')
    await title_entry_point(callback, state, bot)
