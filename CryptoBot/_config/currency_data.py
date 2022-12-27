class StaticCurrency:

    blockchains = {
        "tron": {
            "tokens": [
                {
                    'name': 'USDT',
                    'contract_address': "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
                    "network": {
                        'name': 'mainnet',
                        'mainnet': True
                    },
                    "algorithm": 'TRC-20'
                },
                {
                    'name': 'USDT',
                    'contract_address': "TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdj",
                    "network": {
                        'name': 'nile',
                        'mainnet': False
                    },
                    "algorithm": 'TRC-20'
                },
                {
                    'name': "TRX",
                    'contract_address': None,
                    "network": {
                        'name': 'nile',
                        'mainnet': False
                    },
                    "algorithm": 'TRC-20'
                }
            ]
        },
        "ethereum": {
            "tokens": [
                {
                    'name': "ETH",
                    'contract_address': None,
                    "network": {
                        'name': 'mainnet',
                        'mainnet': True
                    },
                    "algorithm": 'ERC-20'
                },
                {
                    'name': "ETH",
                    'contract_address': None,
                    "network": {
                        'name': 'goerli',
                        'mainnet': False
                    },
                    "algorithm": 'ERC-20'
                },
                {
                    'name': "USDT",
                    'contract_address': "0xdAC17F958D2ee523a2206206994597C13D831ec7",
                    "network": {
                        'name': 'mainnet',
                        'mainnet': True
                    },
                    "algorithm": 'ERC-20'
                }
            ]
        }
    }
