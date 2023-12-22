def display_value(value:float, none: float = -1) -> str:
    '''
    Returns the string representation of value, or "N/A" if value = none
    '''
    if value == none:
        return "N/A"
    return str(value)

def display(
        content:str, indents:int = 0, width:int = None, pos:str = '<') -> str:
    '''
    Returns the content formatted by costumize indents, width and position
    pos should be one of {'<', '^', '>'}
    '''
    if width is None:
        width = len(content)
    return ' '*indents + ('{0: '+ pos + str(width) + '}').format(content)


print(display("hello"))

def account_data_dir(account_name: str):
    return "data/account_data/" + account_name + ".json"

def stock_data_dir(stock_label: str):
    return  "data/stock_data/" + stock_label + ".json"