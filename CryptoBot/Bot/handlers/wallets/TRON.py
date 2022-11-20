from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from Bot.filters.wallet_filters import WalletExists
from Bot.handlers.loading_handler import loader
from Bot.keyboards.wallet_keys import currency_kb
from Bot.states.main_states import MainState
from Bot.states.wallet_states import WalletStates
from Bot.wallet_generator.wallet_generator import wallet_bip44

router = Router()
router.message.filter(StateFilter(MainState.welcome_state, WalletStates))


@router.message(F.text == "USDT (TRC-20)", StateFilter(WalletStates.create_wallet))
async def create_wallet(message: Message, state: FSMContext):
    await loader(message.from_user.id, text="Генерация нового кошелька")
    wallet = wallet_bip44(strength=256)
    a = await wallet.create_TRON()
    ADDRESS_0 = a.get("ADDRESS 0")
    await message.answer(f"Ваш кошелек успешно сгенерирован!\n\n"
                         f"Мнемоническая фраза: <tg-spoiler>{ADDRESS_0.get('Mnemonic')}</tg-spoiler>\n\n"
                         f"Приватный ключ:  <tg-spoiler>{ADDRESS_0.get('PrivateKey')}</tg-spoiler>\n\n"
                         f"Публичный ключ:  {ADDRESS_0.get('PublicKey')}\n\n"
                         f"Адрес кошелька:  {ADDRESS_0.get('Address')}\n\n"
                         )
