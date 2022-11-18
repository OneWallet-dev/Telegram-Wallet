from aiogram.fsm.state import StatesGroup, State


class MainState(StatesGroup):
    welcome_state = State()
