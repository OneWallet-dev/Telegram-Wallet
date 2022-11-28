import asyncio

from aiogram import Router, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from Bot.filters.auth_filter import NotAuthFilter
from Bot.handlers.m_menu_hand import main_menu
from Bot.states.main_states import AuthState
from Bot.utilts.mmanager import MManager
from Databases.DB_Postgres.models import Owner
from Databases.DB_Redis import RedRedis, DataRedis

router = Router()
router.message.filter(NotAuthFilter())


@router.message(~StateFilter(AuthState))
@router.callback_query(~StateFilter(AuthState))
@MManager.garbage_manage()
async def you_need_tb_authenticated(event: Message | CallbackQuery, state: FSMContext):
    await state.set_state(AuthState.need_auth)
    message = event if isinstance(event, Message) else event.message
    msg = await message.answer("<i>К сожалению, ваша сессия истекла.\n"
                               "Авторизируйтесь в боте, отправив ему свой пароль.</i>")
    await MManager.garbage_store(state, msg.message_id)



@router.message(StateFilter(AuthState))
async def password_checking(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    await bot.delete_message(message.chat.id, message.message_id)
    pass_right = await Owner.password_check(session=session, user=message.from_user, text=message.text)
    if pass_right:
        await DataRedis.authorize(message.from_user.id)
        msg = await message.answer("<code>|🟢|🟢|🟢|</code> Вы успешно авторизированы!")
        await asyncio.sleep(0.5)
        await main_menu(message, state, bot)
    else:
        msg = await message.answer("<code>|🔴|🔴|🔴|</code> Авторизация не удалась. Попробуйте снова.")
    await MManager.garbage_store(state, msg.message_id)
