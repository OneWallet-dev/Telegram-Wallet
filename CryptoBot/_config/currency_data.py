class StaticCurrency:

    blockchains = {
        "tron": {
            "tokens": {
                'USDT': {
                    'contract_address': "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
                    "network" : {
                        'name': 'tron',
                        'mainnet': True
                    },
                    "algorithm": 'TRC-20'
                },
                "TRX": {
                    'contract_address': None,
                    "network": {
                        'name': 'tron',
                        'mainnet': True
                    },
                    "algorithm": 'TRC-20'
                }
            }
        },
        "ethereum": {
            "tokens": {
                "ETH": {
                    'contract_address': None,
                    "network": {
                        'name': 'Etherium',
                        'mainnet': True
                    },
                    "algorithm": 'ERC-20'
                }
            }
        }
    }
