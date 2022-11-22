from Bot.models.transaction import Trasaction


class Wallet:
    adress: str
    token: str
    timestamp: str
    name: str
    balance: float
    transaction_list: list[Trasaction]

    def create_trasaction(self):
        pass


class USDTWallet(Wallet):
    def __init__(self, adress: str, token: str, timestamp: str,
                 name: str, balance: float, transaction_list: list[Trasaction]):
        adress: adress
        token: token
        timestamp: timestamp
        name: name
        balance: balance
        transaction_list: transaction_list

    def create_trasaction(self):
        print('Something usefull')
        pass
