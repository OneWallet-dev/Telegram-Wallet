from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from Bot.filters.auth_filter import NotAuthFilter
from Bot.handlers.auth_hand import you_need_tb_authenticated
from Bot.handlers.m_menu_hand import main_menu
from Bot.utilts.mmanager import MManager

router = Router()


# router.message.filter(F.from_user.id.in_(Data.superadmins))

@router.message(Command("admin"))
@MManager.garbage_manage()
async def admin_start(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    await MManager.garbage_store(state, message.message_id)
    await MManager.purge_chat(bot, message_id=message.message_id, chat_id=message.chat.id)
    kb  = InlineKeyboardBuilder()
    kb.add("")
    if await NotAuthFilter()(message):
        await you_need_tb_authenticated(message, state)
    else:
        await message.answer("Добро пожаловть в админ меню")
