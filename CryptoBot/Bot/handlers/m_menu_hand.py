from aiogram import Router, Bot, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from requests import HTTPError
from sqlalchemy.ext.asyncio import AsyncSession

from Bot.handlers.loading_handler import loader
from Bot.handlers.transaction_hand import transaction_start
from Bot.keyboards.main_keys import main_menu_kb
from Bot.keyboards.wallet_keys import main_wallet_keys
from Bot.states.main_states import MainState
from Bot.states.trans_states import TransactionStates
from Bot.states.wallet_states import WalletStates
from Bot.utilts.mmanager import MManager
from Databases.DB_Postgres.models import Owner, Wallet, Address, Token
from crypto.address_gen import Wallet_web3

router = Router()


async def main_menu(update: Message | CallbackQuery, state: FSMContext, bot: Bot):
    message = update if isinstance(update, Message) else update.message
    await MManager.clean(state, bot, message.chat.id)
    await state.clear()
    await state.set_state(MainState.welcome_state)
    bot_name = (await bot.get_me()).full_name
    stick_msg = await message.answer(f'Добро пожаловать в главное меню криптовалютного бота {bot_name}\n'
                                     'Чем я могу вам помочь?', reply_markup=main_menu_kb())
    await MManager.sticker_store(state, stick_msg)


@router.message(F.text == "💹 Мой кошелек")
async def my_wallet_start(message: Message, state: FSMContext, session: AsyncSession):
    tron_text = "Tron:\nАдрес: <code>{}</code>\n\n- TRX: {}"
    eth_text = "Ethereum:\nАдрес: <code>{}</code>\n\n- ETH: {}"
    bit_text = "Bitcoin:\nАдрес: <code>{}</code>\n\n- Bitcoin: {}"
    await state.set_state(WalletStates.create_token)
    owner: Owner = await session.get(Owner, str(message.from_user.id))
    Balance = 0.00
    #tron_addrs, eth_addrs, bitcoin_addrs = str(), str(), str()
    if owner.wallets.get("tron", None) is None:
        generator = Wallet_web3()
        wallets = await generator.generate_all_walllets(message, session)
        print(wallets)
        tron_addrs = wallets.get("tron")
        eth_addrs = wallets.get("eth")
        bitcoin_addrs = wallets.get("bitcoin")
    else:
        Balance = 0.00
        tron_addrs = list(owner.wallets.get("tron").addresses.keys())[0]
        eth_addrs = list(owner.wallets.get("ethereum").addresses.keys())[0]
        bitcoin_addrs = list(owner.wallets.get("bitcoin").addresses.keys())[0]

    tron_text = tron_text.format(tron_addrs, str(Balance))
    eth_text = eth_text.format(eth_addrs, str(Balance))
    bit_text = bit_text.format(bitcoin_addrs, str(Balance))
    sep = "\n<code>——————————————————————</code>\n"
    text = tron_text + sep + eth_text + sep + bit_text
    stick_msg = await message.answer(text, reply_markup=main_wallet_keys())
    await MManager.sticker_store(state, stick_msg)


@router.message(F.text == "👁‍🗨 AML Check")
async def menu_aml_start(message: Message, bot: Bot, state: FSMContext):
    stick_msg = await message.answer('AML проверка',
                                     reply_markup=main_wallet_keys())


@router.message(F.text == "↔️ Транзакции")
async def menu_transaction_start(message: Message, bot: Bot, state: FSMContext):
    await state.set_state(TransactionStates.main)
    await transaction_start(message, bot, state)
