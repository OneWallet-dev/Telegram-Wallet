from aiogram import F, Bot, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from Bot.keyboards.wallet_keys import trans_history_start
from Bot.states.wallet_states import WalletStates
from Bot.utilts.mmanager import MManager
from Dao.models.bot_models import ContentUnit

router = Router()


@router.callback_query(F.data == "full_history", StateFilter(WalletStates))
async def tran_history_start(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(WalletStates.transaction_history_start)
    content: ContentUnit = await ContentUnit(tag="tran_history_start").get()
    placeholder_text = f"Выберите тип транзакций:"
    await MManager.content_surf(event=callback, state=state, bot=bot, content_unit=content,
                                keyboard=trans_history_start(),
                                placeholder_text=placeholder_text)

