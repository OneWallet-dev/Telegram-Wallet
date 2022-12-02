from aiogram.fsm.state import StatesGroup, State


class MainState(StatesGroup):
    welcome_state = State()
    AML_check = State()
    kostul = State()


class RegistrationState(StatesGroup):
    main = State()
    check = State()
    approve = State()


class AuthState(StatesGroup):
    pass_wait = State()
    uid_wait = State()
    start = State()
    need_auth = State()
