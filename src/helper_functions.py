def display_value(value:float, none: float = -1) -> str:
    '''
    Return the string representation of value, or "N/A" if value = none
    '''
    if value == none:
        return "N/A"
    return str(value)

def account_data_dir(account_name: str):
    return "data/account_data/" + account_name + ".json"

def stock_data_dir(stock_label: str):
    return  "data/stock_data/" + stock_label + ".json"