from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from Bot.keyboards.main_keys import main_kb
from Bot.states.main_states import MainState

router = Router()
# router.message.filter(F.from_user.id.in_(Data.superadmins))


@router.message(Command("start"))
async def commands_start(message: Message, state: FSMContext):
    print('Hello')
    await state.set_state(MainState.welcome_state)
    await message.answer('BOT IS ALIVE', reply_markup=main_kb())
