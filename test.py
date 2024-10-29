import yfinance as yf
from src.helper.rounding import *

def check_sell(budget,holding, set_size, kelly_pct, p):
    sell_units = set_size

    if ((1-kelly_pct)*(holding+set_size)-sell_units <= 0):
        return 0, 0
    sell_units = max(sell_units, ceil(-kelly_pct*budget/p + (1-kelly_pct)*(holding+set_size), set_size))
    if sell_units-set_size != 0:
        sell_units -= set_size
    p_h = kelly_pct*budget/((1-kelly_pct)*(holding+set_size)-sell_units)
    return p_h, sell_units


def check_buy(budget,holding, set_size, kelly_pct, p):
    buy_units = set_size
    buy_units = max(buy_units, ceil(kelly_pct*budget/p-(1-kelly_pct)*(holding-set_size), set_size))
    if buy_units-set_size != 0:
        buy_units -= set_size
    p_l = kelly_pct*budget/((1-kelly_pct)*(holding-set_size)+buy_units)
    return p_l, buy_units


budget = 100
holding = 200
set_size = 1
kelly_pct = 0.5
p = 1
p_h, sell_units = check_sell(budget,holding, set_size, kelly_pct, p)
p_l, buy_units = check_buy(budget,holding, set_size, kelly_pct, p)

print(f'Current: bundle value: {holding*p}, budget: {budget}')
print(f'p_l, buy_units: {(p_l, buy_units)}')
print(f'After buy: bundle value: {(holding+buy_units)*p_l}, budget: {budget-p_l*buy_units}')
print(f'p_h, sell_units: {(p_h, sell_units)}')
print(f'After sell: bundle value: {(holding-sell_units)*p_h}, budget: {budget+p_h*sell_units}')