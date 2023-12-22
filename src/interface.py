from . import trading_strategies
from .account import Account
from .stock import Stock
from .trading_strategies import *
from .current import Current
from .my_json import MyJson
from .helper_functions import *



# Type def:
#   Menu    -   {"func": Func, "cmds": list[str], "cmd_handler": list[Cmd]}
#   Cmd     -   [Func, str, str]
#   Func    -   Callable


class Interface:
    '''
    An object that handles processes

    Fields:
        configs             -   dict
        running             -   bool
        trading_straregy    -   BaseTradingStrategy
        account             -   Account
    '''

    def __init__(self, configs: dict, my_json: MyJson) -> None:

        '''
        Initialize account data and tranding strategy
        '''

        self.my_json = my_json

        self.configs = configs

        self.running = True

        account_name = self.configs["account"]

        trading_strategy = self.configs["trading_strategy"]
        
        self.set_trading_strategy(trading_strategy)

        self.set_account(account_name)

        self.set_current()

    
    def set_trading_strategy(self, strategy_name:str):
        self.configs["trading_strategy"] = strategy_name
        trading_strategy_class: BaseTradingStrategy = getattr(
            trading_strategies, strategy_name)
        self.trading_strategy = trading_strategy_class(self.configs)
    
    def set_account(self, account_name):
        '''
        Loads account's data
        '''
        self.configs["account"] = account_name
        account_dir = account_data_dir(account_name)
        account_data = self.my_json.load(account_dir)
        self.account = Account(account_name, account_data)

    
    def set_current(self):
        '''
        Loads current data
        '''
        current_dir = stock_data_dir("current")
        self.current = Current(self.my_json.load(current_dir))
        

    def save_account_data(self):
        account_dir = account_data_dir(self.account.account_name)
        self.my_json.write(account_dir, self.account.in_dict)

    
    def save_setting(self, config_dir):
        self.my_json.write(config_dir, self.configs)

    
    def save_current(self):
        current_dir = stock_data_dir("current")
        self.my_json.write(current_dir, self.current.get_contents()) 


    def proc(self) -> bool:
        '''
        Processes one step
        '''
        pass



class BaseMenuInterface (Interface):
    '''
    An base menu driven interface

    Fields:
        auto_trade      -   bool
        menus           -   dict(Label, Menu)
    '''

    def __init__(self, configs: dict, my_json: MyJson) -> None:
        
        super().__init__(configs, my_json)

        self.auto_trade = configs["auto_trade"]

        self.set_menus()

    
    def set_menus(self):
        '''
        Sets menus' details and handlers
        '''
        
        self.menus = dict()


        main_menu = {"func": self.main_handle,
                    "cmds": ["help", "details",
                             "set",
                             "transfer", "setbudget",
                             "add", "trade", "undo", "remove",
                             "current",
                             "exit"],
                      "cmd_handler": dict()}
        
        self.menus["main_menu"] = main_menu
        main_menu_cmd_handler = main_menu["cmd_handler"]


        main_menu_cmd_handler["help"] = [
            self.show_hints, "help", "view command instructions"]
        
        main_menu_cmd_handler["details"] = [
            self.show_account_details, "details", "view account details"]
        main_menu_cmd_handler["d"] = main_menu_cmd_handler["details"]
        
        main_menu_cmd_handler["set"] = [
            self.to_setting, "set|configs", "go to the setting"]
        main_menu_cmd_handler["configs"] = main_menu_cmd_handler["set"]

        main_menu_cmd_handler["transfer"] = [
            self.transfer, "tf|transfer", "transfer to/from budget"]
        main_menu_cmd_handler["tf"] = main_menu_cmd_handler["transfer"]

        main_menu_cmd_handler["setbudget"] = [
            self.set_budget, "sb|setbudget", "set budget"]
        main_menu_cmd_handler["sb"] = main_menu_cmd_handler["setbudget"]

        
        main_menu_cmd_handler["add"] = [
            self.add_stock, "a|addstock", "add a stock to the bundle"]
        main_menu_cmd_handler["a"] = main_menu_cmd_handler["add"]

        main_menu_cmd_handler["trade"] = [
            self.update_trade, "t|trade", "update new trade"]
        main_menu_cmd_handler["t"] = main_menu_cmd_handler["trade"]

        main_menu_cmd_handler["undo"] = [
            self.undo_trade, "undo", "undo a trade"]
        
        main_menu_cmd_handler["current"] = [
            self.update_current_price, "cp|current", "update stock's current price"]
        main_menu_cmd_handler["cp"] = main_menu_cmd_handler["current"]

        main_menu_cmd_handler["remove"] = [
            self.remove_stock, "r|remove", "remove a stock from the bundle"]
        main_menu_cmd_handler["r"] = main_menu_cmd_handler["remove"]


        main_menu_cmd_handler["exit"] = [
            self.exit, "exit", "exit the program"]


        setting = {"func": self.setting_handle,
                   "cmds": ["help", "details",
                            "account", "strategy", "autotrade",
                            "back"],
                   "cmd_handler": dict()}
        
        self.menus["setting"] = setting
        setting_cmd_handler = setting["cmd_handler"]

        setting_cmd_handler["help"] = [
            self.show_hints, "help", "view command instructions"]
        
        setting_cmd_handler["details"] = [
            self.show_config_details, "d|details", "view configuations"]
        setting_cmd_handler["d"] = setting_cmd_handler["details"]
        
        setting_cmd_handler["account"] = [
            self.switch_account, "a|account", "switch account"]
        setting_cmd_handler["a"] = setting_cmd_handler["account"]

        setting_cmd_handler["strategy"] = [
            self.switch_strategy, "s|strategy", "change strategy"]
        setting_cmd_handler["s"] = setting_cmd_handler["strategy"]

        setting_cmd_handler["autotrade"] = [
            self.set_auto_trade, "auto|autotrade", "set autotrade"]
        setting_cmd_handler["auto"] = setting_cmd_handler["autotrade"]

        setting_cmd_handler["back"] = [
            self.to_main, "back", "go back to the main page"]
        

        self.cur_location = main_menu


    def proc(self):
        '''
        Processes one step
        '''
        self.cur_location["func"]()
        return self.running

    

    def main_handle(self) -> None:
        '''
        Reads cmds (main); prints error message if the cmd is invalid
        '''
        self.basis_handle("main menu")

    
    def setting_handle(self) -> None:
        '''
        Reads cmds (setting); prints error message if the cmd is invalid
        '''
        self.basis_handle("setting")
    
    def basis_handle(self, location: str) -> None:
        print("You are at the " + location + ".")
        print("Type 'help' to see available comands.")

        cmd = self.get_str()
        print()
        self.cur_location["cmd_handler"].get(cmd, [self.cmd_err])[0]()
        print()


    def show_hints(self):
        '''
        Displays commands' instructions
        '''
        print("Avaliable Comands:")
        for cmd in self.cur_location["cmds"]:
            cmd = self.cur_location["cmd_handler"][cmd]
            print(display("[" + cmd[1] + "]", 4, 25), cmd[2], sep = "")
    
            
    def show_account_details(self):
        print(self.account.details(self.current))

    def show_config_details(self):
        print(self.configs)



    def transfer(self):
        amount = self.get_num("Amount: ")
        self.account.budget += amount


    def set_budget(self):
        amount = self.get_num("Amount: ")
        self.account.budget = amount 


    def add_stock(self):
        '''
        Adds a stock into the account's bundle
        '''
        stock_label = self.get_str("Stock Label: ")
        if self.account.contains_stock(stock_label):
            print("Stock", stock_label, "is already in the bundle.")
        else:
            self.account.add_stock(stock_label)

    def update_trade(self) -> None:
        '''
        Updates a trade if the trade is valid; does nothing otherwise
        '''
        stock_label, units, unit_price, other_cost = self.get_trade_info()
        
        if not self.account.contains_stock(stock_label):
            self.account.add_stock(stock_label)
        stock = self.account.get_stock(stock_label)
        

        if not self.account.valid_change(units, unit_price, other_cost)\
            or not stock.valid_change(units, unit_price):
            print("Invalid attempt to trade. Nothing is done.")
        else:
            stock.update_change(units, unit_price, other_cost) 
            self.account.update_change(units, unit_price, other_cost)
    
    def get_trade_info(self) -> tuple[str, float, float, float]:
        '''
        get information of a trade
        '''
        stock_label = self.get_str("Stock label: ")
        units = self.get_num("Units: ")
        unit_price = self.get_num("Unit price: ")
        other_cost = self.get_num("Other cost: ")
        return stock_label, units, unit_price, other_cost
    
    
    def undo_trade(self):
        '''
        attempts to undo a trade
        '''
        stock_label = self.get_str("Stock label: ")
        if not self.account.contains_stock(stock_label):
            print("Stock is not contained in the bundle. Nothing is done.")
            return
        
        stock = self.account.get_stock(stock_label)
        amount_received = stock.undo_change()
        if amount_received == None:
            print("There was no trading on the stock. Nothing is done")
            return

        self.account.budget += amount_received


    def remove_stock(self):
        stock_label = self.get_str("Stock label: ")
        if not self.account.contains_stock(stock_label):
            print("Your bundle doesn't contain ", stock_label,
                  ", Nothing is done.", sep = "")
        elif self.account.is_holding(stock_label):
            print("Your account is still holding ", stock_label,
                  ", nothing is done.", sep = "")
        else:
            self.account.remove_stock(stock_label)


    def update_current_price(self):
        stock_label = self.get_str("Stock label: ")
        price = self.get_num("Current price" \
                             + " (empty input -> delete stock from current): ")
        if price == -1:
            self.current.remove_stock(stock_label)
        else:
            self.current.set_price(stock_label, price)
    

        

    def exit(self):
        self.running = False



    def switch_account(self):
        '''
        Saves current account's data and switch account 
        '''
        self.save_account_data()
        account_name = self.get_str("Account name: ")
        self.set_account(account_name)
        print("Switch to", account_name)

    
    def switch_strategy(self):
        '''
        Attempts to switch trading strategy
        '''
        nstrategy = self.get_str("Strategy name: ")
        if nstrategy not in trading_strategies_set:
            print("Strategy not avaiable.")
            print("Please input one of the following:", trading_strategies_set)
            print("Nothing is done.")
        else:
            self.set_trading_strategy(nstrategy)
            print("Using", nstrategy, "strategy.")
    

    def set_auto_trade(self):
        self.auto_trade = not self.auto_trade
        self.configs["auto_trade"] = self.auto_trade
        print("set auto_trade to", self.auto_trade)


        
    def to_main(self):
        self.cur_location = self.menus["main_menu"]

    def to_setting(self):
        self.cur_location = self.menus["setting"]

    


    def cmd_err(self):
        print("Invalid command. Nothing is done.")


    def get_str(self, display: str = "") -> str:
        return input(display)
    
    def get_num(self, display: str = "", num: type = float) -> float|int:
        def get():
            n = input(display)
            if n == '':
                return -1
            try:
                n = num(n)
            except ValueError:
                print("ValueError: please enter a number")
                return None
            return n
        
        n = None
        while n is None:
            n = get()
        return n
    

