from aiogram.fsm.state import StatesGroup, State


class MainState(StatesGroup):
    welcome_state = State()
    AML_check = State()


class RegistrationState(StatesGroup):
    main = State()
    check = State()
    approve = State()
