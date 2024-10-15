from .stock_statistics import StockStatistics
from . my_json import MyJson
from ..objects.account import Account
from ..objects.stock import Stock 
from ..helper.rounding import *
from ..helper.directory import *
from ..io.io import *
from tqdm import tqdm
import os.path as osp
import operator as op
import pandas as pd
import datetime

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

    Functions:
        default_variables   -> dict
        current_moves       -> dict


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
            'sell_proportion':      0.5,
            'default_step':         10,
            'simulation_budget':    100000
        }

        
    

    def triggered_suggestions(self, stocks_statistics: dict[str, StockStatistics],
                         account: Account, timepoint = -1) -> dict:
        '''
        returns all triggered suggestions at timepoint, sorted by
            categories {'sell','buy'}
        '''
        suggestions = self.suggestions(stocks_statistics, account, timepoint)
        triggered = {'sell': [], 'buy': []}
        for stock_label in suggestions.keys():
            for suggestion in suggestions[stock_label]:
                cur_stat = stocks_statistics[stock_label].get(
                    suggestion[2], beg = timepoint)
                check_fn = suggestion[1]
                trigger_stat = suggestion[3]
                unit_change = suggestion[4]
                if check_fn(cur_stat, trigger_stat):
                    move = [stock_label, unit_change, trigger_stat, suggestion[0]]
                    if unit_change > 0:
                        triggered['buy'].append(move)
                    else:
                        triggered['sell'].append(move)
        return triggered
            



    def suggestions(
            self, stocks_statistics: dict[str, StockStatistics],
            account: Account, timepoint: int|str = -1
    ) -> dict:
        '''
        Produces suggestions for each stock in the account's bundle
        '''
        suggestions = dict()
        if account.bundle_size == 0:
            return suggestions
        budget = account.budget/((account.bundle_size+1)//2)
        for stock_label in account.get_stock_labels():
            stock = account.get_stock(stock_label)
            last_trade = stock.last_trade
            if last_trade is None or last_trade[4] != self.class_name:
                suggestions[stock_label] = self.target_suggestions(
                    stocks_statistics, stock_label,
                    stock.holding, budget, None, timepoint)
            else:
                suggestions[stock_label] = self.target_suggestions(
                    stocks_statistics, stock_label,
                    stock.holding, budget, last_trade[3], timepoint)
        return suggestions


    def target_suggestions(
            self, stocks_statistics: dict[str, StockStatistics],
            stock_label: str, holding: int, budget: float, 
            timepoint1: str|None = None,
            timepoint2: int|str|None = -1
            ) -> list:
        
        '''
        Uses stocks_statistics to provide trading suggestions for a single stock
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

        if timepoint1 is None:
            default_step    = self.variables['default_step']
            timepoint1  = max(0, stock_statistics.get_index(None, timepoint2) - default_step)


        set_size            =   self.variables['set_size']
        min_trade_amount    =   self.variables['min_trade_amount']
        buy_condition       =   self.variables['buy_condition']
        sell_condition      =   self.variables['sell_condition']
        buy_proportion      =   self.variables['buy_proportion']
        sell_proportion     =   self.variables['sell_proportion']


        #print(f'timepoints: {stock_statistics.get("date", timepoint1)} - {stock_statistics.get("date", timepoint2)}')

        local_min   =   stock_statistics.get(
            'min', timepoint1, timepoint2)
        local_max   =   stock_statistics.get(
            'max', timepoint1, timepoint2)
        

        suggestions         =   list()
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
                f'Buy {buy_units} if stock price >= {buy_trigger}',
                op.ge, 'high', buy_trigger, buy_units])
        
        sell_units = ceil(max_sell_units * sell_proportion, set_size)
        if sell_units != 0:
            if sell_units < min_sell_units:
                sell_units = max_sell_units
            suggestions.append([
                f'sell {sell_units} if stock price <= {sell_trigger}',
                op.le, 'low', sell_trigger, -sell_units])

        return suggestions
        

    def simulation(
            self,
            stocks_statistics: dict[str, StockStatistics],
            bundle: list,
            beg:str, end: str) -> pd.DataFrame:
        
        '''
        Preforms a trade simulation
        '''
        
        account_data = {
            "budget": self.variables['simulation_budget'],
            "bundle": {} 
        }
        simulation_result = dict()
        simulation_result['bundle'] = bundle
        simulation_result['trade_counts'] = 0
        simulation_result['log'] = []
        if (len(bundle) == 0):
            return simulation_result


        temp_account = Account('temp_account', account_data)
        stat_beg = '9'
        stat_end = '0'
        for stock in bundle:
            temp_account.add_stock(stock)
            stat_beg = min(stat_beg, stocks_statistics[stock].get('date', 0))
            stat_end = max(stat_end, stocks_statistics[stock].get('date', -1))
        beg = datetime.datetime.strptime(max(beg, stat_beg), f'%Y-%m-%d')
        end = datetime.datetime.strptime(min(end, stat_end), f'%Y-%m-%d')
        
        day_count = (end-beg).days+1
        simulation_result['date'] = [beg + datetime.timedelta(n) for n in range(day_count)]

        simulation_result['value'] = dict()
        simulation_result['value']['account'] = [0 for i in range(day_count)]
        for stock in bundle:
            simulation_result['value'][stock] = [0 for i in range(day_count)]

        

        for i in tqdm(range(day_count)):
            cur = f"{simulation_result['date'][i]}"[:10]
            moves = self.triggered_suggestions(stocks_statistics, temp_account, cur)
            traded = set()
            while len(moves['sell']) != 0 or len(moves['buy']) != 0:
                if len(moves['sell']) != 0:
                    next_move = moves['sell'][0]
                else:
                    next_move = moves['buy'][0]
                label, units, trigger, detail = next_move
                temp_account.get_stock(label).update_change(units, trigger, 0, cur, self.class_name) 
                temp_account.update_change(units, trigger, 0)
                simulation_result['trade_counts'] += 1
                simulation_result['log'].append(f'{cur}: {units} [{label}] at price {trigger}')
                traded.add(label)
                moves = self.triggered_suggestions(stocks_statistics, temp_account, cur)
                moves['sell'] = [move for move in moves['sell'] if not move[0] in traded]
                moves['buy'] = [move for move in moves['buy'] if not move[0] in traded]
            simulation_result['value']['account'][i] = temp_account.account_value(stocks_statistics, cur)
            for stock in bundle:
                simulation_result['value'][stock][i] = stocks_statistics[stock].get('close', cur)

            simulation_result['rate'] = dict()
            base_val = simulation_result['value']['account'][0]
            simulation_result['rate']['account'] = [value/base_val for value in simulation_result['value']['account']]
            for stock in bundle:
                base_val = simulation_result['value'][stock][0]
                simulation_result['rate'][stock] = [value/base_val for value in simulation_result['value'][stock]]
        return simulation_result

                


        


        
        
        


