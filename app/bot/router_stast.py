from aiogram import Router
from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from requests import HTTPError
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud.wallet_crud import WalletCrud
from api.database.postgres import get_session
from api.schemas.wallet_schema import CreateWallet

router = Router()


# router.message.filter(F.from_user.id.in_(Data.superadmins))

@router.message(Command("start"))
async def commands_start(message: Message, session: AsyncSession):
    crud = WalletCrud(session)
    data = CreateWallet(blockchain='tron', owner_id='UF3129049077')
    wallet = await crud.create(data)
    await message.answer(str(wallet))
