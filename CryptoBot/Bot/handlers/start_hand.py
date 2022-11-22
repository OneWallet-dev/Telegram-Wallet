from contextlib import suppress

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, User
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from Bot.keyboards.main_keys import start_kb
from Bot.states.main_states import MainState
from Bot.models.botuser import BotUser
from Databases.DB_Postgres.models import UUser
from bata import Data

router = Router()
bot = Data.main_bot


# router.message.filter(F.from_user.id.in_(Data.superadmins))


@router.message(Command("start"))
async def commands_start(message: Message, state: FSMContext, session: AsyncSession):
    await state.set_state(MainState.welcome_state)
    # await BotUser(session, message.from_user).create()
    user = await UUser().register(session, message.from_user)
    print(user.user_id)
    await message.answer('BOT IS ALIVE', reply_markup=start_kb())

