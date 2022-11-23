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
    owner = await session.get(Owner, message.from_user.id)
    print(owner.wallets)
    text = "Ваш баланс: \n\n"
    for key in owner.wallets:
        address_info = await owner.wallets[key].getBalance()
        text = f"Ваш баланс на кошельке: <code>{owner.wallets[key]}</code>\n\n"
        try:
            for name, info in address_info:
                text = text + f"<b>Токен:</b> <code>{name}</code>\n\n" \
                              f"<b>Баланс:</b> <code>{info.get('balance')}</code>\n\n－－－－－－－－－－－－\n"
        except HTTPError as e:
            print(e)

    await message.answer(text, reply_markup=start_kb())