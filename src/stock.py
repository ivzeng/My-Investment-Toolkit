from .current import Current
from .helper_functions import *




class Stock:
    '''
    An object storing the information of a stock.

    Fields:
        label           -   str;                label of the stock
        holding         -   int;                number of units holding
        cost            -   float;              total cost of the stock
        log             -   list;               trading history
    '''

    def __init__(
            self, label: str, data: dict = dict()
            ) -> None: 
        '''
        Stores stock information
        '''
        self.label          = label
        self.holding        = data.get("holding", 0)
        self.cost           = data.get("cost", 0)
        self.log:list       = data.get("log", [])


    def __str__(self) -> str:
        return "Stock[" + self.label + "]: {Units Holding: " \
            + display_value(self.holding) \
            + ", Cost per Unit: " + display_value(self.unit_cost) \
            + ", Total Cost: " + display_value(self.cost) \
            + "}"
    
    def details(self, current: Current, indents = 0):
        return display("Stock[" + self.label + "]:", indents) + '\n' \
            + display("Units Holding", indents+4, 20) \
            + display(display_value(self.holding), 2, 8) + '\n' \
            + display("Cost per Unit:", indents+4, 20) \
            + display(display_value(self.unit_cost),
                      2, 8) \
            + display("Total Cost:", 4, 20) \
            + display(display_value(self.cost), 2, 8) + '\n' \
            + display("Current Price:", indents+4, 20) \
            + display(display_value(self.get_current_price(current)),
                      2, 8) \
            + display("Current Value:", 4, 20) \
            + display(display_value(self.get_current_value(current)),
                      2, 8) + '\n' \
            + display("Net Profit:", indents+4, 20)  \
            + display(display_value(self.get_net_profit(current)),
                      2, 8)  + '\n' \
            + display("Trade History:", indents+4, 20) +  str(self.log) + '\n'


    @property
    def in_dict(self):
        '''
        Converts object to a dictionary
        '''
        return {
            "holding":          self.holding,
            "cost":             self.cost,
            "log":              self.log,
            }
    
    @property
    def is_empty(self):
        return self.holding == 0
    

    @property
    def unit_cost(self) -> float:
        
        if self.holding == 0:
            return -1
        return round(self.cost/self.holding,2)


    def get_current_price(self, current: Current) -> float:

        return current.get_price(self.label)
    
    def get_current_value(self, current: Current) -> float:
        current_price = self.get_current_price(current)
        if current_price == -1:
            return -1
        return round(current_price*self.holding, 2)

    def get_net_profit(self, current: Current) -> float:
        current_value = self.get_current_value(current)
        if current_value == -1:
            return -1
        return round(current_value - self.cost, 2)

    def get_profit_per_unit(self, current: Current) -> float:
        net_profit = self.get_net_profit(current)

        if self.holding == 0 or net_profit == -1:
            return -1
        return round(net_profit/self.holding, 2)
    

    def valid_change(self, units: int, unit_price: float) -> bool:
        '''
        Determines if a change (or trade) is valid
        '''
        
        return self.holding + units >= 0 and unit_price >= 0


    def update_change(
            self, units: int, unit_price: float, other_cost: float
            ) -> float:
        
        self.holding += units
        self.cost += units*unit_price + other_cost
        self.cost = round(self.cost,2)
        self.log.append([units, unit_price, other_cost])
    
    def undo_change(self) -> float:
        '''
        Recovers the recent change
        Returns the amonge that shoude be added to the account budget
        '''
        if len(self.log) == 0:
            return None
        
        recent_change = self.log.pop()
        self.holding -= recent_change[0]
        self.cost -= recent_change[0] * recent_change[1] + recent_change[2]
        return recent_change[0] * recent_change[1] + recent_change[2]


'''

'''
