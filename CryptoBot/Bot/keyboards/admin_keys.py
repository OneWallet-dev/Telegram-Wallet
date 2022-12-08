from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_admin_kb():
    mark = InlineKeyboardBuilder()
    mark.row((InlineKeyboardButton(text=f"Комиссия", callback_data="confirm_thing")))
    mark.row((InlineKeyboardButton(text=f"Пользователи", callback_data="confirm_thing")))
    mark.row((InlineKeyboardButton(text=f"Сообщения бота", callback_data="mnj_content")))
    mark.row((InlineKeyboardButton(text=f"Администраторы", callback_data="mnj_admins")))
    mark.row((InlineKeyboardButton(text=f"Выход", callback_data="exit")))
    return mark.as_markup(resize_keyboard=True)


def admin_manage_kb():
    mark = InlineKeyboardBuilder()
    mark.row((InlineKeyboardButton(text=f"Добавить администратора", callback_data="addmin")))
    mark.row((InlineKeyboardButton(text=f"Удалить администратора", callback_data="remdmin")))
    mark.row((InlineKeyboardButton(text=f"Назад", callback_data="return")))
    return mark.as_markup(resize_keyboard=True)


def admin_back():
    mark = InlineKeyboardBuilder()
    mark.row((InlineKeyboardButton(text=f"Назад", callback_data="return")))
    return mark.as_markup(resize_keyboard=True)


def admin_approve():
    mark = InlineKeyboardBuilder()
    mark.row((InlineKeyboardButton(text=f"Подтвердить", callback_data="CONFIRM")))
    mark.row((InlineKeyboardButton(text=f"Отменить", callback_data="return")))
    return mark.as_markup(resize_keyboard=True)


def a_content_manage_main_kb():
    mark = InlineKeyboardBuilder()
    mark.row((InlineKeyboardButton(text=f"Получить список всех тэгов", callback_data="all_tags")))
    mark.row((InlineKeyboardButton(text=f"Назад", callback_data="return")))
    return mark.as_markup(resize_keyboard=True)


def content_edit_kb():
    mark = InlineKeyboardBuilder()
    mark.row((InlineKeyboardButton(text=f"Изменить", callback_data="edit")))
    mark.row((InlineKeyboardButton(text=f"Удалить", callback_data="delete")))
    mark.row((InlineKeyboardButton(text=f"Назад", callback_data="return")))
    return mark.as_markup(resize_keyboard=True)


def content_new_kb():
    mark = InlineKeyboardBuilder()
    mark.row((InlineKeyboardButton(text=f"Добавить", callback_data="edit")))
    mark.row((InlineKeyboardButton(text=f"Назад", callback_data="return")))
    return mark.as_markup(resize_keyboard=True)
