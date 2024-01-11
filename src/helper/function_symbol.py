import operator


def get_function(symbol: str):
    return {
        '<': operator.lt,
        '>': operator.gt,
    } [symbol]