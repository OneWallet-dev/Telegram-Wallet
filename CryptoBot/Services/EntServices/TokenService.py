from collections import namedtuple

from sqlalchemy import select

from Bot.utilts.currency_helper import base_tokens
from Bot.utilts.settings import DEBUG_MODE
from Dao.DB_Postgres.session import create_session, AlchemyMaster
from Dao.models.Owner import Owner
from Dao.models.Token import Token


class TokenService:

    @staticmethod
    async def find_address_token(u_id: str, token_name: str, token_network: str, path_index: int = 0):
        """
        Method to get info about token and linked address for given user, token name, token network.

        Returns object with parameters "adress" (Address object) and "token" (Token object)
        """
        result = namedtuple("adress_token", "address token")
        session_connect = await AlchemyMaster.create_session()
        async with session_connect() as session:
            owner: Owner = await session.get(Owner, u_id)
            wallets = owner.wallets
            for wallet in wallets:
                wallet_obj = wallets[wallet]
                for address in wallet_obj.addresses:
                    address_obj = wallet_obj.addresses[address]
                    if address_obj.path_index == path_index:
                        for token in address_obj.tokens:
                            if token.network == token_network:
                                if token.token_name == token_name:
                                    return result(address_obj, token)
                            return result(address_obj, None)

    @staticmethod
    async def get_token(token_name: str, token_network: str) -> Token:
        session_connect = await AlchemyMaster.create_session()
        async with session_connect() as session:
            query = select(Token).filter(Token.token_name == token_name, Token.network == token_network)
            result = (await session.execute(query)).first()
            if result:
                return result[0]

    @staticmethod
    async def form_base_token(name: str):  # Изменить метод, когда улучшится хранилище базовых токенов
        """
        Checks base token library and search for token with given name

        :return Token
        """
        token_dict = base_tokens.get(name)
        network = token_dict.get("network")[0]
        if DEBUG_MODE == True:
            contract_string = 'testnet_contract_address'
        else:
            contract_string = 'contract_address'
        return Token(contract_Id=contract_string, token_name=name, network=network)
