from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from Bot.keyboards.main_keys import start_kb
from Bot.states.main_states import MainState
from Databases.DB_Postgres.models import Owner, Wallet

router = Router()


# router.message.filter(F.from_user.id.in_(Data.superadmins))


@router.message(Command("start"))
async def commands_start(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    await Owner().register(session, message.from_user)
    await main_menu(message, state, bot)


async def main_menu(message: Message, state: FSMContext, bot: Bot):
    await state.set_state(MainState.welcome_state)
    bot_name = (await bot.get_me()).full_name
    await message.answer(f'Добро пожаловать в главное меню криптовалютного бота {bot_name}\n'
                         'Чем я могу вам помочь?', reply_markup=start_kb())
