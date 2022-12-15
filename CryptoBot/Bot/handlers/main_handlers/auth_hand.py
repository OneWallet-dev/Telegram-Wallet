import asyncio

from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from Bot.filters.auth_filter import NotAuthFilter, AuthTimeout
from Bot.handlers.main_handlers.main_menu_hand import main_menu
from Bot.keyboards.main_keys import auth_kb, back_button
from Bot.states.main_states import AuthState, RegistrationState
from Bot.utilts.mmanager import MManager
from Dao.DB_Redis import DataRedis
from Dao.models.bot_models import ContentUnit
from Services.EntServices.OwnerService import OwnerService

router = Router()
router.message.filter(NotAuthFilter())
router.callback_query.filter(NotAuthFilter())


@router.message(~StateFilter(AuthState))
@router.callback_query(~StateFilter(AuthState), ~StateFilter(RegistrationState))
@router.callback_query(F.data == "back", StateFilter(AuthState.uid_wait, RegistrationState))
@MManager.garbage_manage()
async def you_need_tb_authenticated(event: Message | CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(AuthState.need_auth)
    if isinstance(event, CallbackQuery):
        await event.answer()
    content: ContentUnit = await ContentUnit(tag="you_need_auth").get()
    no_content_text = "<i>Здравствуйте! Для работы с ботом необходимо зарегистрироваться или авторизироваться под " \
                      "имеющимся UID</i> "
    await MManager.content_surf(event=event, state=state, bot=bot, content_unit=content,
                                keyboard=auth_kb(),
                                placeholder_text=no_content_text)


@router.callback_query(F.data == "back", StateFilter(AuthState.pass_wait))
@router.callback_query(F.data == "enter", StateFilter(AuthState.need_auth))
async def uid_request(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    await state.set_state(AuthState.uid_wait)
    await state.update_data(edit_msg=callback.message.message_id)
    content: ContentUnit = await ContentUnit(tag="give_me_uid").get()
    no_content_text = "<b>Отправьте мне свой UID:</b>"
    await MManager.content_surf(event=callback, state=state, bot=bot, content_unit=content,
                                keyboard=back_button(),
                                placeholder_text=no_content_text)


@router.message(StateFilter(AuthState.uid_wait))
@MManager.garbage_manage()
async def uid_save(message: Message, state: FSMContext, bot: Bot):
    await bot.delete_message(message.chat.id, message.message_id)
    await state.set_state(AuthState.pass_wait)
    await state.update_data(edit_msg=message.message_id, uid=message.text)

    content: ContentUnit = await ContentUnit(tag="give_me_password").get()
    no_content_text = "<b>Теперь отправьте мне свой пароль</b>"
    await MManager.content_surf(event=message, state=state, bot=bot, content_unit=content,
                                keyboard=back_button(),
                                placeholder_text=no_content_text)


@router.message(StateFilter(AuthState.pass_wait), ~AuthTimeout())
async def password_checking(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    await bot.delete_message(message.chat.id, message.message_id)
    data = await state.get_data()
    pass_right = await OwnerService.password_check(session=session, uid=data['uid'], password=message.text)
    if pass_right:
        await DataRedis.authorize(message.from_user.id, data['uid'])
        content_tag = "auth_succ"
        no_content_text = "<code>|🟢|🟢|🟢|</code> Вы успешно авторизованы!"
    else:
        content_tag = "auth_failed_"
        no_content_text = "<code>|🔴|🔴|🔴|</code> Авторизация не удалась."
        tries = await DataRedis.auth_cooldown(message.from_user.id, add=True)
        if tries <= 2:
            content_tag += "few"
            no_content_text += " Пожалуйста, повторите попытку"
        if tries == 3:
            content_tag += "two_left"
            no_content_text += "\n<i>У вас осталось еще две попытки.</i>"
        if tries == 4:
            content_tag += "last"
            no_content_text += "\n<i>Внимательно проверье свой uid и пароль.</i>\n\n" \
                               "После этой попытки вам придется подождать."
        if tries == 5:
            content_tag += "overdose"
            no_content_text += " Исчерпан лимит попыток. Пожалуйста, попробуйте снова через 10 минут."

    content: ContentUnit = await ContentUnit(tag=content_tag).get()
    await MManager.content_surf(event=message, state=state, bot=bot, content_unit=content,
                                placeholder_text=no_content_text)
    if content_tag == "auth_succ":
        await asyncio.sleep(1)
        await main_menu(message, state, bot)

@router.message(StateFilter(AuthState.pass_wait), AuthTimeout())
async def timeouted(message: Message, bot: Bot):
    msg = await message.answer("Вы исчерпали свой лимит попыток для входа. Попробуйте снова через 10 минут.")
    await asyncio.sleep(5)
    await bot.delete_message(message.chat.id, msg.message_id)
