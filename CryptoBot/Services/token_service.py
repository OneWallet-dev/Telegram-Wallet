from sqlalchemy import select

from Dao.DB_Postgres.session import create_session
from Dao.models.Owner import Owner
from Dao.models.Token import Token


class TokenService:

    @staticmethod
    async def balance_data(user_id: int, token_name: str, token_network: str, path_index: int = 0):
        session_connect = await create_session()
        async with session_connect() as session:
            owner: Owner = await session.get(Owner, str(user_id))
            wallets = owner.wallets
            for wallet in wallets:
                wallet_obj = wallets[wallet]
                for address in wallet_obj.addresses:
                    address_obj = wallet_obj.addresses[address]
                    if address_obj.path_index == path_index:
                        for token in address_obj.tokens:
                            if token.token_name == token_name and token.network == token_network:
                                return dict(address=address, token=token)

    @staticmethod
    async def get_token(contract_id: str):
        session_connect = await create_session()
        async with session_connect() as session:
            token: Token = await session.get(Token, contract_id)
            return token
