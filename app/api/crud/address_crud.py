from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc
from api.api_exceptions.user_exc import CreateUserError
from api.crud.wallet_crud import WalletCrud
from api.database.models.address import Address
from api.schemas.address_schema import CreateAddress, CurrentAddress, AddressOut
from api.schemas.user_schema import UserOut, CurrentUser
from api.schemas.wallet_schema import CurrentWallet


class AddressCrud:
    def __init__(self, db_session: AsyncSession) -> None:
        self._db_session: AsyncSession = db_session

    async def create(self, create_data: CreateAddress) -> CurrentAddress:
        wallet_crud = WalletCrud(self._db_session)
        wallet = await wallet_crud.get_wallet(create_data.wallet_id)

        address = Address(**create_data.dict(exclude_unset=True))

        try:
            self._db_session.add(address)
            new_address: Address = await self._db_session.get(Address, address.id)
            address = CurrentAddress(address=AddressOut(**new_address.__dict__))
            await self._db_session.commit()

            return address
        except exc.IntegrityError:
            await self._db_session.rollback()
            raise CreateUserError

    async def get_address(self, address: str) -> CurrentUser:
        address: Address = await self._db_session.get(Address, address)
        return CurrentUser(user=UserOut(**address.__dict__))


