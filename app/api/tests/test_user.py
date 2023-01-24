from datetime import datetime
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from api.core.security import Security
from api.crud.user_crud import UserCrud
from api.database.models.owner import Owner
from api.schemas.user_schema import CreateUser


@pytest.fixture(scope="session")
def engine():
    engine = create_async_engine("postgresql+asyncpg://TelegramWallet:TelegramWallet@localhost:5454/TelegramWallet")
    yield engine


@pytest_asyncio.fixture
async def session(engine):
    async with AsyncSession(engine) as session:
        yield session


@pytest.mark.asyncio
async def test_create_user(session: AsyncSession):
    user_crud = UserCrud(session)
    password = "pass"
    user = await user_crud.create(CreateUser(password=password))
    owner: Owner = await session.get(Owner, user.user.id)
    assert user.user.created_at < datetime.now()
    assert Security().verify_password(password, owner.password) is True


@pytest.mark.asyncio
async def test_get_user_by_id(session: AsyncSession):
    user_crud = UserCrud(session)
    user_id = 'IC4203941591'
    user = await user_crud.get_user(user_id)
    assert user_id == user.user.id




