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
    eth_text = "ERC-20:\nАдрес: <code>{}</code>\n\n- ETH: {}"
    bit_text = "Bitcoin:\nАдрес: <code>{}</code>\n\n- Bitcoin: {}"
    await state.set_state(WalletStates.create_token)
    owner: Owner = await session.get(Owner, str(message.from_user.id))
    generator = Wallet_web3()
    wallets = await generator.generate_all_walllets()
    tron = wallets.get("tron", None)
    eth = wallets.get("eth", None)
    bitcoin = wallets.get("bitcoin", None)
    Balance = 0.00
    if owner.wallets.get("tron", None) is None:
        await loader(message.from_user.id, "Выполняется генерация кошелька", 4)
        tronaddress: Address = Address(address=tron.get("address_0").get("address"),
                                       private_key=tron.get("address_0").get("private_key"))
        tronwallet = Wallet(blockchain="tron", mnemonic=tron.get("mnemonic"))
        tronwallet.addresses.update({tron.get("address_0").get("address"): tronaddress})
        owner.wallets["tron"] = tronwallet

        ethaddress: Address = Address(address=eth.get("address_0").get("address"),
                                      private_key=eth.get("address_0").get("private_key"))
        ethnwallet = Wallet(blockchain="etherium", mnemonic=eth.get("mnemonic"))
        ethnwallet.addresses.update({eth.get("address_0").get("address"): ethaddress})
        owner.wallets["eth"] = ethnwallet

        bitaddress: Address = Address(address=bitcoin.get("address_0").get("address"),
                                      private_key=bitcoin.get("address_0").get("private_key"))
        bitwallet = Wallet(blockchain="bitcoin", mnemonic=bitcoin.get("mnemonic"))
        bitwallet.addresses.update({bitcoin.get("address_0").get("address"): bitaddress})
        owner.wallets["bit"] = bitwallet

        session.add(owner)
        await session.commit()
        await session.close()
    else:
        Balance = 0.000

    tron_text = tron_text.format(tron.get("address_0").get("address"), str(Balance))
    eth_text = eth_text.format(eth.get("address_0").get("address"), str(Balance))
    bit_text = bit_text.format(bitcoin.get("address_0").get("address"), str(Balance))
    sep = "\n<code>——————————————————————</code>\n"
    text = sep + tron_text + sep + eth_text + sep + bit_text + sep
    stick_msg = await message.answer(text, reply_markup=main_wallet_keys())
    await MManager.sticker_store(state, stick_msg)


@router.message(F.text == "👁‍🗨 AML Check")
async def menu_aml_start(message: Message, bot: Bot, state: FSMContext):
    stick_msg = await message.answer('AML проверка',
                                     reply_markup=main_wallet_keys())


@router.message(F.text == "↔️ Транзакции")
async def menu_transaction_start(message: Message, bot: Bot, state: FSMContext):
    await transaction_start(message, bot, state)
