from aiogram.fsm.state import StatesGroup, State


class WalletStates(StatesGroup):
    choose_currency = State()
    create_wallet = State()
    use_wallet = State()
