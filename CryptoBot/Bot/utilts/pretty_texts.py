
def pretty_balance(balance_dict: dict[str:str]):
    text = 'На кошельке доступно:\n\n'
    for token in balance_dict:
        print(token)
        text += f"- <b> {str(token).upper()}: {balance_dict[token]['balance']}</b> \n"
    return text
