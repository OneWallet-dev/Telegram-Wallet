from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from Bot.utilts.fee_strategy import getFeeStrategy
from Bot.utilts.new_loader import new_loader
from Dao.DB_Postgres.session import create_session
from Dao.models.Address import Address
from Dao.models.Owner import Owner
from Dao.models.Token import Token
from Dao.models.Transaction import Transaction
from Dao.models.Wallet import Wallet
from bata import Data
from crypto.Maker import Maker
from crypto.TronMaker import TronMaker


class Transaction_maker_Factory:
    # TODO ФАбрика мейкеров. Возвращает нужного мейкека
    def getMaker(self,
                 token_name: str,
                 blockchain: str) -> Maker:
        return TronMaker()


class AddressService:

    # REFACTORING 1
    @staticmethod
    async def get_balances(address: str, specific: list[Token] | None = None):
        session_connect = await create_session()
        async with session_connect() as session:
            address_obj: Address = await session.get(Address, address)
            balances = dict()
            twallet = TronMaker()
            for token in address_obj.tokens:
                if (specific and token in specific) or not specific:
                    if token.token_name == 'trx':
                        balance = await twallet.TRX_get_balance(address)
                    elif token.network == 'TRC-20':
                        balance = await twallet.TRC_20_get_balance(token.contract_Id, address)
                    elif token.network == 'TRC-10':
                        balance = await twallet.TRC_10_get_balance(address_obj)
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

        await new_loader(message,chait_id,1,"Проверяем баланс...")
        my_transaction = Transaction(token_contract_id=token.contract_Id,
                                     amount=amount,
                                     from_address=address.address,
                                     to_address=to_address,
                                     address=address)
        service_fee = await getFeeStrategy(address)
        await new_loader(message,chait_id, 1, "Проверяем нагрузку сети...")
        await new_loader(message,chait_id, 1, "Вычисляем блоки...")
        await new_loader(message,chait_id, 2, "Запрос к блокчейну...")
        await new_loader(message,chait_id, 2, "Проверяем количество энергии.")
        await new_loader(message,chait_id, 2, "Проверяем количество энергии..")
        await new_loader(message,chait_id, 2, "Проверяем количество энергии...")
        await new_loader(message,chait_id, 3, "Проверяем количество энергии...")
        await new_loader(message, chait_id, 3, "Формируем транзакци...")
        await new_loader(message, chait_id, 3, "Отправляем запрос в блокчейн...")
        await new_loader(message, chait_id, 4, "Совершаем транзакцию...")

        transaction_maker = Transaction_maker_Factory().getMaker(token.token_name, address.wallet.blockchain)
        transaction_dict = await transaction_maker.transfer(my_transaction, service_fee=service_fee)
        if transaction_dict:
            my_transaction.tnx_id = transaction_dict.get("txn_id")
            my_transaction.service_fee = service_fee
            my_transaction.status = transaction_dict.get("status")
            await new_loader(message, chait_id, 5, "Совершаем транзакцию...")
            session = await create_session()
            await new_loader(message, chait_id, 5, "Завершаем транзакцию...")
            async with session() as session:
                local_object = await session.merge(my_transaction)
                session.add(local_object)
                await session.commit()
                await session.close()
                await new_loader(message, chait_id, 6, "Записываем данные в базу...")
                await new_loader(message, chait_id, 7, "Записываем данные в базу...")
                return my_transaction

        else:
            return "Недостаточно средств"
