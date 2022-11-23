from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from requests import HTTPError
from sqlalchemy.ext.asyncio import AsyncSession

from Bot.keyboards.main_keys import start_kb
from Bot.states.main_states import MainState
from Databases.DB_Postgres.models import Owner, Wallet

router = Router()


# router.message.filter(F.from_user.id.in_(Data.superadmins))


@router.message(Command("start"))
async def commands_start(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    await Owner().register(session, message.from_user)
    await main_menu(message, state, bot)


async def main_menu(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    await state.set_state(MainState.welcome_state)
    bot_name = (await bot.get_me()).full_name
    await message.answer(f'Добро пожаловать в главное меню криптовалютного бота {bot_name}\n'
                         'Чем я могу вам помочь?', reply_markup=start_kb())


@router.message(Command("generate"))
async def commands_start(message: Message, state: FSMContext, session: AsyncSession):
    owner: Owner = await session.get(Owner, message.from_user.id)
    wallet = await owner.createWallet(blockchain="tron", session=session)
    await message.answer(str(wallet), reply_markup=start_kb())

@router.message(Command("getMyWallets"))
async def commands_start(message: Message, state: FSMContext, session: AsyncSession):
    owner: Owner = await session.get(Owner, message.from_user.id)
    print(owner.wallets)
    for key in owner.wallets:
        print(owner.wallets[key])
        await message.answer(str(owner.wallets[key]), reply_markup=start_kb())

@router.message(Command("getbalance"))
async def commands_start(message: Message, state: FSMContext, session: AsyncSession):
    owner: Owner = await session.get(Owner, message.from_user.id)
    print(owner.wallets)
    for key in owner.wallets:
        try:
            print(await owner.wallets[key].getBalance())
        except HTTPError as e:
            print(e)

        await message.answer(str(owner.wallets[key]), reply_markup=start_kb())

@router.message(Command("createTransaction"))
async def commands_start(message: Message, state: FSMContext, session: AsyncSession):
    owner: Owner = await session.get(Owner, message.from_user.id)
    print(owner.wallets)
    for key in owner.wallets:
        if owner.wallets[key].blockchain=="tron":
            my_wallet: Wallet = owner.wallets[key]
            break

    text = await my_wallet.createTransaction(session,"TY1Qry1UD6YG6qWMqPz45jkNWKzzisCkTT",5)
    await message.answer(text, reply_markup=start_kb())