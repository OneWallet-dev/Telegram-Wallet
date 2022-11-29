from aiogram.fsm.state import StatesGroup, State

class TransactionStates(StatesGroup):
    main = State()


class Trs_transfer(StatesGroup):
    main = State()

class Trs_exchange(StatesGroup):
    main = State()

class Trs_withdrawal(StatesGroup):
    main = State()
