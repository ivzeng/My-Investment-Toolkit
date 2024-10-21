def convert_to(n:str, t:type, default = None, exception = None):
    try:
        n = t(n)
    except:
        if n is None or len(n) == 0:
            return default
        return exception
    return n
