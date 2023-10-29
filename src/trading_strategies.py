from src.stock import Stock
from src.account import Account

# Type def
#   Amount          -   positive number
#   UnitCount       -   nonnegative integer  
#   TSuggestion     -   [UnitCount, Amount]

trading_strategies_set  = {"BaseTradingStrategy", "SimpleTrade"}

class BaseTradingStrategy:
    '''
    An object preforming a trading strategy.

    Fields:
        
    '''
    
    def __init__(self) -> None:
        pass

    def current_suggestions(
            self, account:Account
            ) -> list[list, list]:
        '''
        returns two list of trading suggestions (buy and sell), each sorted
            by the priority
        '''
        pass


class SimpleTrade (BaseTradingStrategy):
    '''
    buy as much as possible if a stock have relatively low price;
    sell all if the price of a stock increases by 50% of the difference
        between its original price and the expected upper bound
    '''
    
    def __init__(self) -> None:
        super().__init__()
    
    