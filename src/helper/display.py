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



