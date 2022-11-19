from contextlib import suppress

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from Bot.keyboards.main_keys import start_kb
from Bot.states.main_states import MainState
from Databases.models.user import Users
from bata import Data

router = Router()
bot = Data.main_bot


# router.message.filter(F.from_user.id.in_(Data.superadmins))


@router.message(Command("start"))
async def commands_start(message: Message, state: FSMContext, session: AsyncSession):
    user = Users()
    user.user_id = message.from_user.id
    user.username = message.from_user.username
    user.first_name = message.from_user.first_name
    session.add(user)
    with suppress(IntegrityError):
        await session.commit()

    await state.set_state(MainState.welcome_state)
    await message.answer('BOT IS ALIVE', reply_markup=start_kb())
