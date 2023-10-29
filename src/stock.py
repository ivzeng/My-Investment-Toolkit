# Type def
#   Label       -   string
#   Amount      -   positive number
#   UnitCount   -   non-negative integers
#   Trade       -   list[Trade_type, Unitcount, Amount]
#   TradeType   -   "B" | "S" | "T"     buy | sell | tax



class Stock:
    '''
    An object storing the information of a stock.

    Fields:
        label           -   Label;              label of the stock
        units_hold      -   UnitCount;          number of stocking holding
        cost            -   Amount;             total cost for buying the stock
        dividend_earn   -   Amount;             total amount of cash dividend    
        trading_log     -   list[Trade];        trading history
        current_price   -   Amount;             current unit price
        expected_bound  -   [Amount, Amount]    estimated extreme price of stock
    '''

    def __init__(
            self, label: str, data: dict = dict()
            ) -> None:
        
        self.label          = label
        self.units_hold     = data.get("units_hold", 0)
        self.cost           = data.get("cost", 0)
        self.log:list       = data.get("log", [])
        self.current_price  = data.get("current_price", 1)
        self.expected_range = data.get(
            "expected_range", 
            [self.current_price*0.5, self.current_price*2]
        )


    def __str__(self) -> str:
        return "Stock[" + self.label + "]:\n   Units Holding: " \
            + str(self.units_hold) \
            + "\n   Cost:" + str(self.cost) \
            + "\n   Cost per unit: " + str(self.cost_per_unit) \
            + "\n   Trade History: " + str(self.log) \
            + "\n   Recent Unit Price: " + str(self.current_price) + "\n"

    @property
    def in_dict(self):
        return {
            "units_hold": self.units_hold,
            "cost": self.cost,
            "log": self.log,
            "current_price": self.current_price,
            "expected_range": self.expected_range
            }
    

    @property
    def cost_per_unit(self) -> float:
        if self.units_hold == 0:
            return -1

        return round(self.cost/self.units_hold,2)
    
    @property
    def current_value(self) -> float:

        return round(self.units_hold*self.current_price, 2)

    @property
    def gains(self) -> float:

        return round(self.current_value - self.cost, 2)

    @property
    def gains_per_unit(self) -> float:

        if self.units_hold == 0:
            return -1
        return round(self.gains/self.units_hold, 2)
    

    def varify_trade(
            self, units: int, value: float, budget: float
            ) -> bool:
        
        return budget - value >= 0 \
            and self.units_hold + units >= 0 \
            and units*value >= 0


    def update_change(
            self, units: int = 0, value: float = 0, new_price: float = 0
            ) -> float:
        
        if new_price > 0:
            self.current_price = new_price
        
        self.units_hold += units
        self.cost += value
        self.cost = round(self.cost,2)

        if value == 0 and units == 0:
            print("stock price changes to", new_price)
            return
        
        change_info = [None, units, value]
        if units == 0:
            change_info[0] = "T"
            print("pay tax with a cost of", value)
        elif units > 0:
            change_info[0] = "B"
            print("bought", units, "stocks with a cost of", value)
        else:
            change_info[0] = "S"
            print("sold", -units, "stocks with a gain of", -value)
        self.log.append(change_info)

        return -value
    
    def undo_change(self):
        if len(self.log) == 0:
            print("There was no trading on the stock. Nothing is done")
            return
        
        recent_change = self.log.pop()
        self.units_hold -= recent_change[1]
        self.cost -= recent_change[2]

        print("Undo", recent_change)

        return recent_change[2]
        



    def add_dividend(
            self,
            cash_dividend_per_unit:float = 0,
            stock_dividend_per_unit:float = 0
            ) -> float:
        
        cash_dividend = self.units_hold*cash_dividend_per_unit
        self.cost -= cash_dividend
        self.current_price -= cash_dividend

        stock_dividend = self.units_hold*stock_dividend_per_unit
        self.units_hold += stock_dividend

        self.log.append(["D", stock_dividend, -cash_dividend])

        print("receive", cash_dividend,
                "amount of cash dividend and", 
                self.units_hold*stock_dividend_per_unit,
                "stock divend")

        return round(self.units_hold*cash_dividend_per_unit, 2)




'''
bc = Stock("bc")
print(bc)
budget = 3000
budget += bc.update_change(300, 1226.02)
print("Budget:", round(budget,2))
print("Earning:", bc.gains())
print(bc)

budget += bc.update_change(400, 1565.04)
print("Budget:", round(budget,2))
print("Earning:", bc.gains())
print(bc)


budget += bc.add_dividend(cash_dividend_per_unit=0.232)
print("Budget:", round(budget,2))
print("Earning:", bc.gains())
print(bc)

budget += bc.update_change(-500, -1893.06)
budget += bc.update_change(0, 11.6)
print("Budget:", round(budget,2))
print("Earning:", bc.gains())
print(bc)

budget += bc.update_change(-200, -786.58)
budget += bc.update_change(0, 4.64)
print("Budget:", round(budget,2))
print("Earning:", bc.gains())
print(bc)

'''
