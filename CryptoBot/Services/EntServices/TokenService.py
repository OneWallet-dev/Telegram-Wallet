from collections import namedtuple

from sqlalchemy import select

from Dao.DB_Postgres.session import create_session
from Dao.models.Owner import Owner
from Dao.models.Token import Token


class TokenService:

    @staticmethod
    async def find_address_token(u_id: str, token_name: str, token_network: str, path_index: int = 0):
        """
        Method to get info about token and linked address for given user, token name, token network.

        Returns dict {"address": Address object with given token, "token": Token object}
        """
        result = namedtuple("adress_token", "address token")
        session_connect = await create_session()
        async with session_connect() as session:
            owner: Owner = await session.get(Owner, u_id)
            wallets = owner.wallets
            for wallet in wallets:
                wallet_obj = wallets[wallet]
                for address in wallet_obj.addresses:
                    address_obj = wallet_obj.addresses[address]
                    if address_obj.path_index == path_index:
                        for token in address_obj.tokens:
                            if token.token_name == token_name and token.network == token_network:
                                return result(address_obj, token)
                        return result(address_obj, None)

    @staticmethod
    async def get_token(token_name: str, token_network: str):
        session_connect = await create_session()
        async with session_connect() as session:
            token: Token = (await session.execute(select(Token).filter(Token.token_name == token_name,
                                                                      Token.network == token_network))).first()
            return token
