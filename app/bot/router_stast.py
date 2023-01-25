from aiogram import Router
from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from requests import HTTPError
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud.address_crud import AddressCrud
from api.crud.user_crud import UserCrud
from api.crud.wallet_crud import WalletCrud
from api.database.postgres import get_session
from api.schemas.address_schema import CreateAddress
from api.schemas.user_schema import CreateUser
from api.schemas.wallet_schema import CreateWallet

router = Router()


# router.message.filter(F.from_user.id.in_(Data.superadmins))
@router.message(Command("create_user"))
async def commands_start(message: Message, session: AsyncSession):
    crud = UserCrud(session)
    data = CreateUser(password='1234')
    user = await crud.create(data)
    await message.answer(str(user))

@router.message(Command("create_wallet"))
async def commands_start(message: Message, session: AsyncSession):
    crud = WalletCrud(session)
    data = CreateWallet(blockchain='tron', owner_id='TG3168131234')
    wallet = await crud.create(data)
    await message.answer(str(wallet))

@router.message(Command("create_address"))
async def commands_start(message: Message, session: AsyncSession):
    crud = AddressCrud(session)
    data = CreateAddress(address='142112', wallet_id=2, custom_name='w1', private_key='321')
    address = await crud.create(data)
    await message.answer(str(address))

