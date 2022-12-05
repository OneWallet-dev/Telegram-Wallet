from aiogram.types import Message


from Bot.utilts.fee_strategy import getFeeStrategy
from Bot.utilts.new_loader import new_loader
from CryptoMakers.Maker import Maker
from CryptoMakers.Tron.Tron_TRC10_Maker import Tron_TRC10_Maker
from CryptoMakers.Tron.Tron_TRC20_Maker import Tron_TRC20_Maker
from Dao.DB_Postgres.session import create_session
from Dao.models.Address import Address
from Dao.models.Owner import Owner
from Dao.models.Token import Token
from Dao.models.Transaction import Transaction
from Dao.models.Wallet import Wallet


class Transaction_maker_Factory:
    # TODO ФАбрика мейкеров. Возвращает нужного мейкека
    def getMaker(self,
                 token_name: str,
                 network: str) -> Maker:
        if network == "TRC-20":
            return Tron_TRC20_Maker()
        if network == "TRC-10":
            return  Tron_TRC10_Maker()
        if token_name == "trx":
            return  Tron_TRC10_Maker()

class AddressService:

    @staticmethod
    async def get_balances(address: str, specific: list[Token] | None = None): # TODO полностью переделать, получать из фабрики, вызывать только getBalance
        session_connect = await create_session()
        async with session_connect() as session:
            address_obj: Address = await session.get(Address, address)
            balances = dict()
            for token in address_obj.tokens:
                if (specific and token in specific) or not specific:
                    if token.token_name == 'trx':
                        twallet = Tron_TRC10_Maker()
                        balance = await twallet.TRX_get_balance(address)
                        frozen_fee = address_obj.get_address_freezed_fee('trx')
                        balance = balance - frozen_fee
                    elif token.network == 'TRC-20':
                        twallet = Tron_TRC20_Maker()
                        balance = await twallet.get_balance(token.contract_Id, address)
                        frozen_fee = address_obj.get_address_freezed_fee('TRC-20')
                        balance = balance - frozen_fee
                    elif token.network == 'TRC-10':
                        twallet = Tron_TRC10_Maker()
                        balance = await twallet.get_balance(address_obj)
                        frozen_fee = address_obj.get_address_freezed_fee('TRC-10')
                        balance = balance - frozen_fee
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

        await new_loader(message, chait_id, 1, "Проверяем баланс...")
        service_fee = await getFeeStrategy(address)

        my_transaction = Transaction(token_contract_id=token.contract_Id,
                                     amount=amount,
                                     from_address=address.address,
                                     to_address=to_address,
                                     address=address,
                                     service_fee=service_fee)
        await new_loader(message, chait_id, 1, "Проверяем нагрузку сети...")
        await new_loader(message, chait_id, 1, "Вычисляем блоки...")
        await new_loader(message, chait_id, 2, "Запрос к блокчейну...")
        await new_loader(message, chait_id, 2, "Проверяем количество энергии.")
        await new_loader(message, chait_id, 2, "Проверяем количество энергии..")
        await new_loader(message, chait_id, 2, "Проверяем количество энергии...")
        await new_loader(message, chait_id, 3, "Проверяем количество энергии...")
        await new_loader(message, chait_id, 3, "Формируем транзакци...")
        await new_loader(message, chait_id, 3, "Отправляем запрос в блокчейн...")
        await new_loader(message, chait_id, 4, "Совершаем транзакцию...")
        transaction_maker = Transaction_maker_Factory().getMaker(token.token_name, token.network)
        transaction_dict = await transaction_maker.transfer(my_transaction)
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
