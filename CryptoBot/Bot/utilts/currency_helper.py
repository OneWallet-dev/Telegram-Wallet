base_tokens = {
    'USDT': {'network': ['TRC-20'], 'blockchain': 'tron',
             'contract_address': "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
             'testnet_contract_address': "TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdj"},
    'trx': {'network': ['TRC-20'], 'blockchain': 'tron', 'contract_address': "trx", 'testnet_contract_address': "trx"},
    'ETH': {'network': ['ERC-20'], 'blockchain': 'etherium', 'contract_address': "eth", 'testnet_contract_address': "eth"}
}


blockchains = {
    "tron": {
        "networks": ["TRC-20", "TRC-10"],
        "base_coin": 'TRX'
    },
    'ethereum': {
        "networks": ["ERC-20"],
        "base_coin": 'ETH '
    },
    'bitcoin': {
        "networks": ["bitcoin"],
        "base_coin": 'BTC'
    }
}

