from aiogram.fsm.state import StatesGroup, State


class WalletStates(StatesGroup):
    choose_currency = State()
    create_wallet = State()
    use_wallet = State()


class WalletSendMoney(StatesGroup):
    send_money_start = State()
    send_money_where = State()
    send_money_how_many = State()
    send_money_confirm = State()