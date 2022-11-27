from sre_parse import State

from aiogram.fsm.state import StatesGroup


class TransState(StatesGroup):
    main = State()
