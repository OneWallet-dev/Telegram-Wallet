from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc

from api.api_exceptions.user_exc import CreateUserError
from api.api_exceptions.wallet_exc import WalletExist
from api.core.security import Security
from api.crud.user_crud import UserCrud
from api.database.models.blockchain import Blockchain
from api.database.models.owner import Owner
from api.database.models.wallet import Wallet
from api.schemas.user_schema import CreateUser, UserOut, CurrentUser
from api.schemas.wallet_schema import CreateWallet, CurrentWallet, WalletOut


class WalletCrud:
    def __init__(self, db_session: AsyncSession) -> None:
        self._db_session: AsyncSession = db_session

    async def create(self, create_data: CreateWallet) -> CurrentWallet:
        owner_crud = UserCrud(self._db_session)
        owner = await owner_crud.get_user(create_data.owner_id)
        if owner.wallets.get(create_data.blockchain) is not None:
            raise WalletExist

        wallet = Wallet(**create_data.dict(exclude_unset=True),
                        mnemonic=Security().generate_mnemonic())
        owner.wallets[create_data.blockchain] = wallet

        try:
            self._db_session.add(owner)
            await self._db_session.commit()
            return CurrentWallet(wallet=WalletOut(**wallet.__dict__))
        except exc.IntegrityError:
            await self._db_session.rollback()
            raise CreateUserError

    async def get_wallet(self, wallet_id: str) -> CurrentWallet:
        wallet: Wallet = await self._db_session.get(Owner, wallet_id)
        return CurrentWallet(user=WalletOut(**wallet.__dict__))
