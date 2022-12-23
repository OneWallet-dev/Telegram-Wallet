import asyncio
from contextlib import suppress

import requests
from aiogram.types import Message
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from Bot.exeptions.wallet_ex import DuplicateToken
from Bot.utilts.fee_strategy import getFeeStrategy
from Bot.handlers.service_handlers.loader_hand import loader

from Dao.DB_Postgres.session import AlchemyMaster
from Dao.models.Address import Address
from Dao.models.Owner import Owner
from Dao.models.Token import Token
from Dao.models.Transaction import Transaction
from Dao.models.Wallet import Wallet
from Services.CryptoMakers.ETH.Eth_Maker import ETH_maker
from Services.CryptoMakers.Maker import Maker
from Services.CryptoMakers.Tron.Tron_User_Maker import Tron_TRC_Maker
from bata import Data


class Maker_Factory:
    @staticmethod
    def get_maker(token: Token, network=None) -> Maker:
        maker = None

        if len(token.contract_Id) <= 3: #TODO: КОСТЫЛЬ КОСТЫЛЬ КОСТЫЛЬ КОСТЫЛЬ КОСТЫЛЬ КОСТЫЛЬ
            token.contract_Id = None

        print(token.contract_Id)
        if token.network == "TRC-20":
            maker = Tron_TRC_Maker()
        if token.network == "ERC-20":
            maker = ETH_maker('polygon-testnet')
        return maker


class AddressService:

    @staticmethod
    async def get_address_balances(address: str, specific: list[Token] | None = None):
        # TODO полностью переделать, получать из фабрики, вызывать только getBalance
        session_connect = await AlchemyMaster.create_session()
        async with session_connect() as session:
            address_obj: Address = await session.get(Address, address)
            balances = dict()

            for token in address_obj.tokens:
                if (specific and token in specific) or not specific:
                    b_maker = Maker_Factory.get_maker(token)
                    balance = await b_maker.get_balance(address=address, contract=token.contract_Id)
                    balances.update({token.token_name: balance})
        return balances

    @staticmethod
    def get_address_for_transaction(owner: Owner, blockchain_name: str, contract_id: str) -> Address or None:
        wallet: Wallet = owner.wallets[blockchain_name]
        addresses: list = wallet.addresses.values()
        for address in addresses:
            if contract_id in address.token_list:
                return address

    @staticmethod
    async def createTransaction(address: Address,
                                amount: float,
                                token: Token,
                                to_address: str,
                                message: Message = None,
                                chait_id: int = None) -> Transaction or str:

        await loader(message, chait_id, 1, "Проверяем баланс...")
        service_fee = await getFeeStrategy(address)

        my_transaction = Transaction(token_contract_id=token.contract_Id,
                                     amount=amount,
                                     from_address=address.address,
                                     to_address=to_address,
                                     network=token.network,
                                     address=address,
                                     service_fee=service_fee)
        await loader(message, chait_id, 1, "Проверяем нагрузку сети...")
        await loader(message, chait_id, 1, "Вычисляем блоки...")
        await loader(message, chait_id, 2, "Запрос к блокчейну...")
        await loader(message, chait_id, 2, "Проверяем количество энергии.")
        await loader(message, chait_id, 2, "Проверяем количество энергии..")
        await loader(message, chait_id, 2, "Проверяем количество энергии...")
        await loader(message, chait_id, 3, "Проверяем количество энергии...")
        await loader(message, chait_id, 3, "Формируем транзакци...")
        await loader(message, chait_id, 3, "Отправляем запрос в блокчейн...")
        await loader(message, chait_id, 4, "Совершаем транзакцию...")
        transaction_maker = Maker_Factory.get_maker(token)
        transaction_dict = await transaction_maker.transfer(my_transaction)
        transaction_dict = transaction_dict.txn_resp
        print("TANSFER", transaction_dict)
        if transaction_dict.get("status") == "SUCCESS":
            if transaction_dict.get("result") != "FAILED":
                my_transaction.tnx_id = transaction_dict.get("txn")
                my_transaction.service_fee = service_fee
                my_transaction.status = transaction_dict.get("status")
                await loader(message, chait_id, 5, "Совершаем транзакцию...")
                session = await AlchemyMaster.create_session()
                await loader(message, chait_id, 5, "Завершаем транзакцию...")
                async with session() as session:
                    local_object = await session.merge(my_transaction)
                    session.add(local_object)
                    await session.commit()
                    await session.close()
                    await loader(message, chait_id, 6, "Записываем данные в базу...")
                    await loader(message, chait_id, 7, "Записываем данные в базу...")
                    return my_transaction
            else:
                await message.answer("Ошибка транзакции")

        else:
            return "Недостаточно средств"

    @staticmethod
    async def add_currency(address: str | Address, token: Token):
        session_connect = await AlchemyMaster.create_session()
        async with session_connect() as session:
            if isinstance(address, str):
                address: Address = await session.get(Address, address)

            token_exists: Token = await session.get(Token, token.contract_Id)
            if token_exists:
                token = token_exists

            if token not in address.tokens:
                address.tokens.append(token)
                session.add(address)
                with suppress(IntegrityError):
                    await session.commit()
            else:
                raise DuplicateToken

    @staticmethod
    async def remove_currency(address: str, contract_id: str):
        session_connect = await AlchemyMaster.create_session()
        async with session_connect() as session:
            address_obj: Address = await session.get(Address, address)
            token_obj: Token = await session.get(Token, contract_id)
            for ad_token in address_obj.tokens:
                if token_obj == ad_token:
                    address_obj.tokens.remove(ad_token)
                    session.add(address_obj)
                    await session.commit()

    @staticmethod
    async def get_address_transactions(address: Address) -> dict[str, Transaction]:
        session = await AlchemyMaster.create_session()
        counter = 0
        resp = requests.get(
            f"https://apilist.tronscanapi.com/api/accountv2?address={address.address}&source=search&word=TQzqehsVt7UENiBXBWwHUwDF9GPWvhxyvA&session-id=590c839e-f6a8-458e-953c-2e183eb8e884&order=0")
        json_dict = resp.json()
        transactions_in: int = json_dict["transactions_in"]
        transactions: int = json_dict["transactions"]
        # add
        if not transactions_in == "0":
            with_price_tokens = json_dict["withPriceTokens"]
            for el in with_price_tokens:
                if el["tokenName"] == "USDT" and float(el["balance"]) > 0:
                    float_balance = float(el["balance"]) * 1_000_000
                    print(f"{float_balance}       {el['tokenName']}")
                    print(address.address)
