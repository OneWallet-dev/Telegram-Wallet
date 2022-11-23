from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from Bot.filters.wallet_filters import ChainOwned
from Bot.keyboards.wallet_keys import create_wallet_kb, currency_kb, use_wallet_kb
from Bot.states.main_states import MainState
from Bot.states.wallet_states import WalletStates
from Bot.utilts.cleaner import Cleaner
from Databases.DB_Postgres.models import Owner, Wallet

router = Router()
router.message.filter(StateFilter(MainState.welcome_state, WalletStates))


@router.message(F.text == "💹 Кошельки", StateFilter(MainState.welcome_state))
async def choose_currency(message: Message, state: FSMContext):
    await message.answer('Выберите криптовалюту, с которой вы хотите совершать операции:',
                         reply_markup=currency_kb())


@router.callback_query(ChainOwned())
async def use_wallet(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()
    await state.set_state(WalletStates.use_wallet)
    owner: Owner = await Owner.get(session, callback.from_user)
    wallet: Wallet = owner.wallets[callback.data]
    msg = await callback.message.answer(f'Вы владеете кошельком в сети <b>{callback.data}</b>:\n'
                                        f'<code>{wallet.wallet_address}</code>\n\n'
                                        f'Правда тут должно выдавать не адрес, а баланс и кнопки для взаимодействия.',
                                        reply_markup=use_wallet_kb())
    await Cleaner.store(state, msg.message_id)


@router.callback_query(~ChainOwned())
async def do_you_want_it(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(WalletStates.create_wallet)
    msg = await callback.message.answer(f'У вас нет кошелька в сети <b>{callback.data}</b>. Хотите завести?\n\n'
                                        f'Пусть нажмет одну лишнюю кнопку, не будем создавать кошелек по умолчанию.',
                                        reply_markup=create_wallet_kb(callback.data))
    await Cleaner.store(state, msg.message_id)


@router.message(F.text.startswith("🪙 Открыть кошелек в сети"), StateFilter(WalletStates.create_wallet))
async def choose_currency(message: Message, state: FSMContext):
    await state.set_state(WalletStates.use_wallet)
    await message.answer('Создан кошелек:', reply_markup=use_wallet_kb())
