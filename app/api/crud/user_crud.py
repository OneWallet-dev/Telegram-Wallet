from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc

from api.api_exceptions.user_exc import CreateUserError
from api.core.security import Security
from api.database.models.owner import Owner
from api.schemas.user_schema import CreateUser, UserOut, CurrentUser


class UserCrud:
    def __init__(self, db_session: AsyncSession) -> None:
        self._db_session: AsyncSession = db_session

    async def create(self, create_data: CreateUser) -> CurrentUser:
        owner = Owner(password=Security().hash_password(create_data.password),
                      id=Security().generate_uuid())

        try:
            self._db_session.add(owner)
            new_owner: Owner = await self._db_session.get(Owner, owner.id)
            new_owner: CurrentUser = CurrentUser(user=UserOut(**new_owner.__dict__))
            await self._db_session.commit()

            return new_owner
        except exc.IntegrityError:
            await self._db_session.rollback()
            raise CreateUserError

    async def get_user(self, user_id: str) -> Owner:
        owner: Owner = await self._db_session.get(Owner, user_id)
        return owner


