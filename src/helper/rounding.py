import math


def floor(val: float|int, set_size: int = 1) -> int:
    return math.floor(val/set_size) * set_size

def ceil(val: float|int, set_size: int = 1) -> int:
    return math.ceil(val/set_size) * set_size