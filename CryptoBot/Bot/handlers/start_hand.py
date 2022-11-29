from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from requests import HTTPError
from sqlalchemy.ext.asyncio import AsyncSession

from Bot.filters.auth_filter import NotAuthFilter
from Bot.handlers.auth_hand import you_need_tb_authenticated
from Bot.handlers.m_menu_hand import main_menu
from Bot.handlers.registration_hand import registration_start
from Bot.keyboards.main_keys import main_menu_kb
from Bot.utilts.mmanager import MManager
from Dao.models.Token import Token
from Dao.models.Owner import Owner
from Dao.models.Wallet import Wallet
from Dao.models.Address import Address

router = Router()


# router.message.filter(F.from_user.id.in_(Data.superadmins))

@router.message(Command("start"))
@MManager.garbage_manage()
async def commands_start(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    await MManager.garbage_store(state, message.message_id)
    user_check = await session.get(Owner, str(message.from_user.id))
    if not user_check:
        await registration_start(message, state)
    elif await NotAuthFilter()(message):
        await you_need_tb_authenticated(message, state)
    else:
        await main_menu(message, state, bot)


@router.message(Command("generate"))
async def commands_start(message: Message, state: FSMContext, session: AsyncSession):
    owner: Owner = await session.get(Owner, message.from_user.id)
    wallet = await owner.createWallet(blockchain="tron", session=session)
    await message.answer(str(wallet), reply_markup=main_menu_kb())


@router.message(Command("getMyWallets"))
async def commands_start(message: Message, state: FSMContext, session: AsyncSession):
    owner: Owner = await session.get(Owner, str(message.from_user.id))
    print(owner.wallets)

    for key in owner.wallets:
        wallet: Wallet = owner.wallets[key]
        print(wallet.tokens)
        await message.answer(str(owner.wallets[key]), reply_markup=main_menu_kb())


@router.message(Command("getbalance"))
async def commands_start(message: Message, state: FSMContext, session: AsyncSession):
    owner: Owner = await session.get(Owner, str(message.from_user.id))
    print(owner.wallets)
    for key in owner.wallets:
        try:
            print(await owner.wallets[key].getBalance())
        except HTTPError as e:
            print(e)

        await message.answer(str(owner.wallets[key]), reply_markup=main_menu_kb())


@router.message(Command("createTransaction"))
async def commands_start(message: Message, state: FSMContext, session: AsyncSession):
   owner: Owner = await session.get(Owner, str(message.from_user.id))

   # owner.wallets["tron"] = Wallet(blockchain="tron")
   address: Address = Address(address="token_address")
   owner.wallets["tron123"] = Wallet(blockchain="tron")
   token: Token = Token(contract_Id = "token_contract", token_name = "token_name")
   address.tokens.append(token)
   wallet_tron: Wallet = owner.wallets["tron123"]
   wallet_tron.addresses[address.address]=address

   session.add(owner)
   await session.commit()
   await session.close()

@router.message(Command("test"))
@MManager.garbage_manage(store=True, clean=True)
async def command_test(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    await Owner.add_currency(session, message.from_user, 'USDT', 'aaaa')
    """Please use this function if you want to test something new"""
    pass
