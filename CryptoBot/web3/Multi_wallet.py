from web3 import *
"""Что если объеденить все кошельки в один класс?"""


class wallet(Tron_wallet, Eth_wallet, Bitcoin_wallet):
    pass

