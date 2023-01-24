from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc

from api.api_exceptions.user_exc import CreateUserError
from api.core.security import Security
from api.database.models.owner import Owner
from api.database.models.wallet import Wallet
from api.schemas.user_schema import CreateUser, UserOut, CurrentUser
from api.schemas.wallet_schema import CreateWallet, CurrentWallet, WalletOut


class UserCrud:
    def __init__(self, db_session: AsyncSession) -> None:
        self._db_session: AsyncSession = db_session

    def create(self, create_data: CreateWallet) -> CurrentWallet:
        wallet = Wallet(**create_data.dict(), mnemonic=Security().generate_mnemonic())

        try:
            self._db_session.add(wallet)
            new_wallet: Wallet = await self._db_session.get(Wallet, wallet.id)
            await self._db_session.commit()

            return CurrentWallet(wallet=UserOut(**new_wallet.__dict__))
        except exc.IntegrityError:
            await self._db_session.rollback()
            raise CreateUserError

    def get_wallet(self, wallet_id: int) -> CurrentWallet:
        wallet: Wallet = await self._db_session.get(Owner, wallet_id)
        return CurrentWallet(user=WalletOut(**wallet.__dict__))
