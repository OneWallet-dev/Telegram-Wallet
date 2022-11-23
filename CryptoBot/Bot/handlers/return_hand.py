from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from Bot.handlers.start_hand import main_menu
from Bot.handlers.wallet_hand import choose_currency
from Bot.keyboards.wallet_keys import currency_kb
from Bot.states.wallet_states import WalletStates
from Bot.utilts.cleaner import Cleaner

router = Router()


@router.message(F.text == '⬅️ Назад')
async def step_back(message: Message, bot: Bot, state: FSMContext):
    # state_str = await state.get_state()
    # if state_str in ("WalletStates:create_wallet", "WalletStates:use_wallet"):
    await Cleaner.store(state, message.message_id)
    await Cleaner.clean(state, bot, message.chat.id)
    await main_menu(message=message, state=state, bot=bot)

