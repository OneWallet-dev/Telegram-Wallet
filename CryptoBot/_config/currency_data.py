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
                }
            ]
        }
    }
