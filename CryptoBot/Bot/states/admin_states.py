from aiogram.fsm.state import StatesGroup, State


class AdminState(StatesGroup):
    main = State()
    admins_manage = State()
    admins_manage_add = State()
    admins_manage_remove = State()
    content_select = State()
    content_update = State()
    content_remove = State()
