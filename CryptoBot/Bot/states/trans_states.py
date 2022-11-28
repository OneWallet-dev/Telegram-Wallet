from sre_parse import State

from aiogram.fsm.state import StatesGroup


class TransactionStates(StatesGroup):
    main = State()
