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
from Databases.DB_Postgres.models import Owner, Wallet

router = Router()


# router.message.filter(F.from_user.id.in_(Data.superadmins))

@router.message(Command("start"))
@MManager.garbage_manage()
async def commands_start(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    await MManager.garbage_store(state, message.message_id)
    user_check = await Owner.get(session, message.from_user)
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
    owner: Owner = await session.get(Owner, message.from_user.id)
    print(owner.wallets)
    for key in owner.wallets:
        print(owner.wallets[key])
        await message.answer(str(owner.wallets[key]), reply_markup=main_menu_kb())


@router.message(Command("getbalance"))
async def commands_start(message: Message, state: FSMContext, session: AsyncSession):
    owner: Owner = await session.get(Owner, message.from_user.id)
    print(owner.wallets)
    for key in owner.wallets:
        try:
            print(await owner.wallets[key].getBalance())
        except HTTPError as e:
            print(e)

        await message.answer(str(owner.wallets[key]), reply_markup=main_menu_kb())


@router.message(Command("createTransaction"))
async def commands_start(message: Message, state: FSMContext, session: AsyncSession):
    owner: Owner = await session.get(Owner, message.from_user.id)
    print(owner.wallets)
    for key in owner.wallets:
        if owner.wallets[key].blockchain == "tron":
            my_wallet: Wallet = owner.wallets[key]
            break

    text = await my_wallet.createTransaction(session, "TY1Qry1UD6YG6qWMqPz45jkNWKzzisCkTT", 5)
    await message.answer(text, reply_markup=main_menu_kb())


@router.message(Command("test"))
@MManager.garbage_manage(store=True, clean=True)
async def command_test(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    """Please use this function if you want to test something new"""
    pass
