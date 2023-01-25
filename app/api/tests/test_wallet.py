from datetime import datetime
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from api.api_exceptions.user_exc import UserNotFound
from api.core.security import Security
from api.crud.user_crud import UserCrud
from api.crud.wallet_crud import WalletCrud
from api.database.models.owner import Owner
from api.schemas.user_schema import CreateUser
from api.schemas.wallet_schema import CreateWallet


@pytest.fixture(scope="session")
def engine():
    engine = create_async_engine("postgresql+asyncpg://TelegramWallet:TelegramWallet@localhost:5454/TelegramWallet")
    yield engine


@pytest_asyncio.fixture
async def session(engine):
    async with AsyncSession(engine) as session:
        yield session


@pytest.mark.asyncio
async def test_create_wallet(session: AsyncSession):
    wallet_crud = WalletCrud(session)
    data = CreateWallet(blockchain='tron', owner_id='UF3129049077')
    owner: Owner = await session.get(Owner, data.owner_id)
    if owner is None:
        raise UserNotFound()

    wallet = await wallet_crud.create(CreateWallet(blockchain=data.blockchain, owner_id=data.owner_id))



@pytest.mark.asyncio
async def test_get_user_by_id(session: AsyncSession):
    user_crud = UserCrud(session)
    user_id = 'IC4203941591'
    user = await user_crud.get_user(user_id)
    assert user_id == user.user.id




