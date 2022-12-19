from aiogram import F, Bot, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from Bot.handlers.Transaction_metods.transfer_hand import start_transfer
from Bot.keyboards.wallet_keys import add_token_kb
from Bot.states.wallet_states import WalletStates
from Bot.utilts.mmanager import MManager
from Dao.models.bot_models import ContentUnit

router = Router()


@router.callback_query(F.data == "send", StateFilter(WalletStates))
async def replenish_choose_currency(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(WalletStates.send_start)
    content: ContentUnit = await ContentUnit(tag="some_send_tag").get()
    placeholder_text = f"Выберите валюту для отправки:"
    await MManager.content_surf(event=callback, state=state, bot=bot, content_unit=content,
                                keyboard=add_token_kb(),
                                placeholder_text=placeholder_text)

