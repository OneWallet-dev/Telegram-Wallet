from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc
from api.api_exceptions.addess_exc import AddressExist, AddressCreateError
from api.database.models.address import Address
from api.database.models.wallet import Wallet
from api.schemas.address_schema import CreateAddress, CurrentAddress, AddressOut
from api.schemas.user_schema import UserOut, CurrentUser


class AddressCrud:
    def __init__(self, db_session: AsyncSession) -> None:
        self._db_session: AsyncSession = db_session

    async def create(self, create_data: CreateAddress) -> CurrentAddress:

        wallet: Wallet = await self._db_session.get(Wallet, create_data.wallet_id)
        address = Address(**create_data.dict(exclude_unset=True))
        wallet.addresses.append(address)
        try:
            self._db_session.add(wallet)
            await self._db_session.commit()
            return CurrentAddress(address=AddressOut(**address.__dict__))
        except exc.IntegrityError:
            await self._db_session.rollback()
            raise AddressExist
        except exc:
            raise AddressCreateError

    async def get_address(self, address: str) -> Address:
        address: Address = await self._db_session.get(Address, address)
        return address


