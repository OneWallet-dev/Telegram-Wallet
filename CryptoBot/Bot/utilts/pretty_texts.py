
def pretty_balance(balance_dict: dict[str:float]):
    text = 'На кошельке доступно:\n\n'
    for token in balance_dict:
        text += f"- <b> {token}: {round(balance_dict[token], 5)}</b> \n"
    return text




