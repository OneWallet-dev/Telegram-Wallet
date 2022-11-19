from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from Bot.keyboards.main_keys import main_kb
from Bot.states.main_states import MainState
from Databases.models.user import Users
from bata import Data

router = Router()
bot = Data.main_bot


# router.message.filter(F.from_user.id.in_(Data.superadmins))


@router.message(Command("start"))
async def commands_start(message: Message, state: FSMContext):
    session = await bot.get_db_session()
    async with session() as session:
        await session.merge(Users(user_id=message.from_user.id,
                                  username=message.from_user.username,
                                  first_name=message.from_user.first_name))
        await session.commit()
    print('Hello')
    await state.set_state(MainState.welcome_state)
    await message.answer('BOT IS ALIVE', reply_markup=main_kb())
