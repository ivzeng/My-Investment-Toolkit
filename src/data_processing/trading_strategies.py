from .stock_statistics import StockStatistics
from . my_json import MyJson
from ..objects.account import Account
from ..objects.stock import Stock 
from ..helper.rounding import *
from ..helper.directory import *
from ..io.io import *
import os.path as osp
import operator as op

trading_strategies_set = {
    'BaseTradingStrategy',
    'AdjustingPosition'}
 

class BaseTradingStrategy:
    '''
    An trading stragety that suggests to buy a1% of budget when the stock price
        increases by b1%, and to sell a2% of holding if the stock price
        decreases by b2%
    
    Fields:
        variables           -   dict
        stock_info          -   dict
    '''
    def __init__(self,  my_json: MyJson) -> None:
        data = my_json.load(
            strategy_data_dir(self.class_name),
            {'variables': self.default_variables()})
        self.variables = data['variables']
        
    
    @property
    def class_name(self):
        return self.__class__.__name__

    def default_variables(self) -> dict:
        return {
            'set_size':             100,
            'min_trade_amount':     1000,
            'buy_condition':        0.05,
            'sell_condition':       -0.05,
            'buy_proportion':       0.5,
            'sell_proportion':      0.5
        }
    

    def current_moves(self, stocks_statistics: dict[str, StockStatistics],
                         account: Account) -> dict:
        '''
        returns the current moves suggested by the strategy, sorted by
            categories {'sell','buy'}
        '''
        prev_suggestions = self.suggestions(stocks_statistics, account, 1)
        current_moves = {'sell': [], 'buy': []}
        for stock_label in prev_suggestions.keys():
            current_moves[stock_label] = []
            for suggestion in prev_suggestions[stock_label]:
                cur_statistics = stocks_statistics[stock_label].get_variate(
                    suggestion[2], beg = -1)
                if suggestion[1](cur_statistics, suggestion[3]):
                    move = [stock_label, suggestion[4], suggestion[3]]
                    if suggestion[4] > 0:
                        current_moves['buy'].append(move)
                    else:
                        current_moves['sell'].append(move)
        return current_moves
            



    def suggestions(
            self, stocks_statistics: dict[str, StockStatistics],
            account: Account, delay: int = 0
    ) -> dict:
        '''
        Produces the suggestions for each stock in the account's bundle
        '''
        suggestions = dict()
        if account.bundle_size == 0:
            return suggestions
        budget = account.budget/((account.bundle_size+1)//2)
        for stock_label in account.get_stock_labels():
            stock = account.get_stock(stock_label)
            last_trade = stock.last_trade
            if last_trade is None or last_trade[4] != self.class_name:
                suggestions[stock_label] = self.give_suggestion(
                    stocks_statistics, stock_label,
                    stock.holding, budget, None, delay
                )
            else:
                suggestions[stock_label] = self.give_suggestion(
                    stocks_statistics, stock_label,
                    stock.holding, budget, last_trade[3], delay
                )
        return suggestions


    def give_suggestion(
            self, stocks_statistics: dict[str, StockStatistics],
            stock_label: str, holding: int, budget: float, 
            last_timepoint: str|None = None,
            delay:int = 0
            ) -> list:
        
        '''
        Uses stocks_statistics to provide suggestion for a stock
        A suggestion is a list
                [   description:        str,
                    condition_func:     callable,
                    cur_statistics:     str,
                    trigger_price:      float,
                    units_change:       int         ]
        '''
        stock_statistics = stocks_statistics.get(stock_label, None)

        if stock_statistics is None:
            return []

        if last_timepoint is None:
            last_timepoint = stock_statistics.get_variate('date', -10-delay)
        

        current_timepoint = stock_statistics.get_variate('date', -1-delay)

        set_size            =   self.variables['set_size']
        min_trade_amount    =   self.variables['min_trade_amount']
        buy_condition       =   self.variables['buy_condition']
        sell_condition      =   self.variables['sell_condition']
        buy_proportion      =   self.variables['buy_proportion']
        sell_proportion     =   self.variables['sell_proportion']


        local_min   =   stock_statistics.get(
            'min', last_timepoint, current_timepoint)
        local_max   =   stock_statistics.get(
            'max', last_timepoint, current_timepoint)

        return self.generate_suggestions(
            set_size, min_trade_amount,
            buy_condition, sell_condition,
            buy_proportion, sell_proportion,
            local_min, local_max,
            budget, holding)
        
        
    

    def generate_suggestions(
            self,
            set_size:           int,
            min_trade_amount:   float,
            buy_condition:      float,
            sell_condition:     float,
            buy_proportion:     float,
            sell_proportion:    float,
            local_min:          float,
            local_max:          float,
            budget:             float,
            holding:            int
    ) -> list:
        
        suggestions = list()
        buy_trigger         =   round(local_min * (1 + buy_condition), 2)
        sell_trigger        =   round(local_max * (1 + sell_condition), 2)

        min_buy_units       =   ceil(min_trade_amount/buy_trigger, set_size)
        max_buy_units       =   floor(budget/buy_trigger, set_size)
        min_sell_units      =   ceil(min_trade_amount/sell_trigger, set_size)
        max_sell_units      =   holding


        buy_units = ceil(max_buy_units * buy_proportion, set_size)
        if buy_units != 0:
            if buy_units < min_buy_units:
                buy_units = max_buy_units
            suggestions.append([
                str(buy_units) + ' if stock price >= ' + str(buy_trigger),
                op.ge, 'high', buy_trigger, buy_units])
        
        sell_units = ceil(max_sell_units * sell_proportion, set_size)
        if sell_units != 0:
            if sell_units < min_sell_units:
                sell_units = max_sell_units
            suggestions.append([
                str(-sell_units) + ' if stock price <= ' + str(sell_trigger),
                op.le, 'low', sell_trigger, -sell_units])

        return suggestions


