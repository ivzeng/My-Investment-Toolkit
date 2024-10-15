from .stock import Stock
from .current import Current
from ..data_processing.trading_strategies import *
from ..helper.display import *



class Account:
    '''
    An object stores the account informations

    Fields:
        budget      -   float;                  available funds
        bundle      -   dict[str, Stock]        set of stocks
    '''

    def __init__(self, account_name: str, data: dict[str, float|dict]) -> None:
        '''
        Loads account data 
        '''
        self.account_name = account_name
        self.budget = data.get("budget", 0)
        self.bundle: dict[str, Stock] = dict()

        for label in data.get("bundle", dict()).keys():
            self.bundle[label] = Stock(label, data["bundle"][label])

    def __str__(self) -> str:
        
        return "Account[" + self.account_name + "]:\n" \
            + display("Available Funds:", 4, 20) \
            + display(str(self.budget), 2, 8)
    
    def details(self, current: Current):
        return self.__str__() + "\n"\
                + display(self.bundle_details(current), 4, 20) + "\n"
    
    def bundle_details(self, current: Current) -> str:
        bundle_in_str = "List of Stocks:\n"
        for label in self.bundle.keys():
            bundle_in_str +=  self.bundle[label].details(current, 8) + '\n'
        return bundle_in_str
    
    def account_value(self, stock_statistics: dict[str, StockStatistics], timepoint: int|str = -1) -> int|float:
        value = self.budget
        for label in self.bundle.keys():
            if label in stock_statistics.keys():
                value += self.bundle[label].holding * stock_statistics[label].get('close', timepoint)
            else:
                value += self.bundle[label].cost
        return value


    
    @property
    def in_dict(self) -> str:
        '''
        Converts the class into a dictionary
        '''
        bundle_in_dict = dict()
        for label in self.bundle.keys():
            bundle_in_dict[label] = self.bundle[label].in_dict
        
        return {"budget": self.budget,
                "bundle": bundle_in_dict}
    
    @property
    def bundle_size(self):
        return len(self.bundle)

    def contains_stock(self, label: str) -> bool:
        '''
        Returns true iff stock with name label is in the bundle
        '''
        return label in self.bundle.keys()
    
    def units_holding(self, label: str) -> int:
        '''
        Returns the number of units the account is holding
        '''
        if not self.contains_stock(label):
            return 0
        return self.get_stock(label).holding
    
    def is_holding(self, label: str) -> bool:
        '''
        Returns true iff the account is holding some units of the stock label
        '''
        return label in self.bundle.keys()\
              and not self.bundle[label].is_empty


    def add_stock(self, label:str) -> None:
        '''
        Adds stock with name label into the bundle
        '''
        if not self.contains_stock(label):
            self.bundle[label] = Stock(label)


    def get_stock(self, label:str) -> Stock | None:
        
        return self.bundle.get(label, None)
    
    def get_stock_labels(self) -> list[str]:

        return [stock_label for stock_label in self.bundle.keys()]


    def remove_stock(self, label:str):

        self.bundle.pop(label)


    def valid_change(self, units, unit_price, other_cost) -> bool:

        return self.budget - units * unit_price - other_cost >= 0
    

    def update_change(self, units, unit_price, other_cost):

        self.budget -= units * unit_price + other_cost

