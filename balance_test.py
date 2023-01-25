from datetime import datetime

from eth_utils import encode_hex, function_abi_to_4byte_selector, add_0x_prefix
from web3._utils.contracts import encode_abi
from web3._utils.abi import get_abi_output_types
from web3 import Web3
from web3.types import HexBytes


web3 = Web3(Web3.HTTPProvider("https://bsc-dataseed1.defibit.io"))

TOKENS_BALANCE_ABI = {"inputs": [{"internalType":"address","name":"owner","type":"address"},{"internalType":"address[]","name":"contracts","type":"address[]"}],"name":"tokensBalance","outputs":[{"components":[{"internalType":"bool","name":"success","type":"bool"},{"internalType":"bytes","name":"data","type":"bytes"}],"internalType":"struct BalanceScanner.Result[]","name":"results","type":"tuple[]"}],"stateMutability":"view","type":"function"}
TOKENS_BALANCE_SELECTOR = encode_hex(function_abi_to_4byte_selector(TOKENS_BALANCE_ABI))
tokens_balance_output_types = get_abi_output_types(TOKENS_BALANCE_ABI)

tokens_to_check = [
    '0x55d398326f99059fF775485246999027B3197955', # USDT
    '0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d', # USDC
]

user_address = "0x2A647559a6c5dcB76ce1751101449ebbC039b157"

def check_eth_balance():
    encoded_data = encode_abi(
        w3=web3,
        abi=TOKENS_BALANCE_ABI,
        arguments=(user_address, [t for t in tokens_to_check]),  # аргументы функции tokensBalance
        data=TOKENS_BALANCE_SELECTOR,
    )
    tx = {
      "to": "0x83cb147c13cBA4Ba4a5228BfDE42c88c8F6881F6",  # адрес контракта BalanceScanner
      "data": encoded_data
    }

    tx_raw_data = web3.eth.call(tx)
    output_data = web3.codec.decode(tokens_balance_output_types, tx_raw_data)[0]

    res = {}
    for token_address, (_, bytes_balance) in zip(tokens_to_check, output_data):
        wei_balance = web3.codec.decode(["uint256"], HexBytes(bytes_balance))[0]
        res[token_address] = wei_balance
    print(res)


start = datetime.now()
check_eth_balance()
end = datetime.now()
print("bsc_balances", end - start)
