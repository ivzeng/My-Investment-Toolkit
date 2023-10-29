from src.stock import Stock
from src.trading_strategies import *

# Type def
#   Label       -   string
#   Amount      -   positive number


class Account:
    '''
    An object stores the account informations

    Fields:
        budget      -   Amount;                 available funds
        bundle      -   dict[Label, Stock]      set of stocks
    '''

    def __init__(self, account_name: str, data: dict[str, float|dict]) -> None:
        self.account_name = account_name
        self.budget = data.get("budget", 0)
        self.bundle: dict[str, Stock] = dict()

        for label in data.get("bundle", dict()).keys():
            self.bundle[label] = Stock(label, data["bundle"][label])

    def __str__(self) -> str:
        bundle_in_str = "List of Stocks:\n"
        for label in self.bundle.keys():
            bundle_in_str +=  str(self.bundle[label]) + '\n'
        
        return "Account[" + self.account_name + "]" \
            + "\nAvailable Funds: " + str(self.budget) \
            + "\nStock Value: " + str(self.current_stock_value) \
            + "\nTotal Value: " + str(self.current_total_value) \
            + "\nProfit:      " + str(self.current_profit) \
            + "\n\n" + bundle_in_str
    
    @property
    def in_dict(self) -> str:
        bundle_in_dict = dict()
        for label in self.bundle.keys():
            bundle_in_dict[label] = self.bundle[label].in_dict
        
        return {"budget": self.budget,
                "bundle": bundle_in_dict}



    @property
    def current_stock_value(self) -> float:
        value = 0
        for stock in self.bundle.values():
            value += stock.current_value
        return value
    

    @property
    def current_total_value(self) -> float:
        return self.budget + self.current_stock_value
    

    @property
    def current_profit(self) -> float:
        value = 0
        for stock in self.bundle.values():
            value += stock.gains
        return value
    
    def contains_stock(self, label: str) -> bool:
        return label in self.bundle.keys()

    def add_stock(self, label:str) -> None:
        if not self.contains_stock(label):
            self.bundle[label] = Stock(label)


