from aiogram import Router, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from Bot.handlers.main_handlers.transaction_menu_hand import transaction_start
from Bot.handlers.main_handlers.wallet_handlers.main_wallet_hand import my_wallet_start
from Bot.keyboards.main_keys import main_menu_kb
from Bot.keyboards.wallet_keys import main_wallet_keys
from Bot.states.main_states import MainState
from Bot.states.trans_states import TransactionStates
from Bot.utilts.ContentService import ContentService
from Bot.utilts.mmanager import MManager
from Dao.DB_Redis import DataRedis
from Dao.models.bot_models import ContentUnit

router = Router()


async def title_entry_point(update: Message | CallbackQuery, state: FSMContext, bot: Bot):
    message = update if isinstance(update, Message) else update.message
    await MManager.clean(state, bot, message.chat.id)
    await state.set_state(MainState.welcome_state)

    content: ContentUnit = await ContentUnit(tag="title_message").get()
    placeholder = "Заглавное сообщение бота."
    msg = await ContentService.send(content, bot, chat_id=message.chat.id,
                                    keyboard=main_menu_kb(), placeholder_text=placeholder)
    await MManager.garbage_store(state, msg.message_id, important=True)


async def main_menu(update: Message | CallbackQuery, state: FSMContext, bot: Bot):
    message = update if isinstance(update, Message) else update.message
    await state.set_state(MainState.welcome_state)
    u_id = await DataRedis.find_user(update.from_user.id)

    content: ContentUnit = await ContentUnit(tag="main_menu").get()
    content.text = content.text.format(u_id=u_id)
    placeholder = "Это главное меню бота."
    await MManager.content_surf(message, state, bot, content, keyboard=main_menu_kb(), placeholder_text=placeholder)


@router.message(F.text == "💹 Мой кошелек")
async def menu_wallet_start(message: Message, bot: Bot, state: FSMContext, session: AsyncSession):
    await my_wallet_start(event=message, state=state, bot=bot)


@router.message(F.text == "👁‍🗨 AML Check")
async def menu_aml_start(message: Message, bot: Bot, state: FSMContext):
    stick_msg = await message.answer('AML проверка',
                                     reply_markup=main_wallet_keys())


@router.message(F.text == "↔️ Транзакции")
async def menu_transaction_start(message: Message, bot: Bot, state: FSMContext):
    await state.set_state(TransactionStates.main)
    await transaction_start(message, state)
