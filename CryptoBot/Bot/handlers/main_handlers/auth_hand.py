from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from Bot.filters.auth_filter import NotAuthFilter
from Bot.handlers.main_handlers.main_menu_hand import main_menu
from Bot.keyboards.main_keys import auth_kb, back_button
from Bot.states.main_states import AuthState, RegistrationState
from Bot.utilts.mmanager import MManager
from Dao.DB_Redis import DataRedis
from Dao.models.Owner import Owner

router = Router()
router.message.filter(NotAuthFilter())
router.callback_query.filter(NotAuthFilter())


@router.message(~StateFilter(AuthState))
@router.callback_query(~StateFilter(AuthState), ~StateFilter(RegistrationState.main))
@MManager.garbage_manage()
async def you_need_tb_authenticated(event: Message | CallbackQuery, state: FSMContext):
    await state.set_state(AuthState.need_auth)
    if isinstance(event, CallbackQuery):
        await event.answer()
    message = event if isinstance(event, Message) else event.message
    msg = await message.answer("<i>Здравствуйте! Для работы с ботом необходимо зарегистрироваться "
                               "или авторизироваться под имеющимся UID</i>", reply_markup=auth_kb())
    await MManager.garbage_store(state, msg.message_id)


@router.callback_query(F.data == "back", StateFilter(AuthState.uid_wait, RegistrationState.main))
async def back_again(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    await state.set_state(AuthState.need_auth)
    await bot.edit_message_text(text="<b>Вы можете войти в бота или создать новый аккаунт:</b>",
                                chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                reply_markup=auth_kb())


@router.callback_query(F.data == "back", StateFilter(AuthState.pass_wait))
@router.callback_query(F.data == "enter", StateFilter(AuthState.need_auth))
async def uid_request(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    await state.set_state(AuthState.uid_wait)
    await state.update_data(edit_msg=callback.message.message_id)
    await bot.edit_message_text(text="<b>Отправьте мне свой UID:</b>",
                                chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                reply_markup=back_button())


@router.message(StateFilter(AuthState.uid_wait))
@MManager.garbage_manage()
async def uid_save(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    await bot.delete_message(message.chat.id, message.message_id)
    await state.set_state(AuthState.pass_wait)
    edit_id = (await state.get_data())['edit_msg']
    await state.update_data(edit_msg=message.message_id, uid=message.text)
    await bot.edit_message_text(text="<b>Теперь отправьте мне свой пароль</b>",
                                chat_id=message.chat.id,
                                message_id=edit_id,
                                reply_markup=back_button())


@router.message(StateFilter(AuthState.pass_wait))
async def password_checking(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    await bot.delete_message(message.chat.id, message.message_id)
    data = await state.get_data()
    pass_right = await Owner.password_check(session=session, uid=data['uid'], password=message.text)
    if pass_right:
        await DataRedis.authorize(message.from_user.id, data['uid'])
        msg = await message.answer("<code>|🟢|🟢|🟢|</code> Вы успешно авторизованы!")
        await main_menu(message, state, bot)
    else:
        msg = await message.answer("<code>|🔴|🔴|🔴|</code> Авторизация не удалась. Попробуйте снова.")
    await MManager.garbage_store(state, msg.message_id)
