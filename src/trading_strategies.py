from src.stock import Stock
from src.account import Account
import pandas as pd
import os.path as osp

# Type def
#   Amount          -   positive number
#   UnitCount       -   nonnegative integer  
#   TSuggestion     -   [UnitCount, Amount] 



trading_strategies_set = {"BaseTradingStrategy", "SimpleReweight"}
 


class BaseTradingStrategy:
    '''
    An object preforming a trading strategy.

    Fields:
        
    '''
    
    def __init__(self, configs: dict) -> None:
        pass


        


class SimpleReweight(BaseTradingStrategy):
    '''
    suggest the proportion of budget investing on a stock based on 
        prediction by a regression model between the expected price
        changes in a number of days and the current price
    '''
    
    def __init__(self, configs: dict) -> None:
        super().__init__(configs)
        self.days = configs["strategy_configs"]["SimpleReweight"]["days"]
    
