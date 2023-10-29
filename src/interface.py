import json
import os.path as osp
from . import trading_strategies
from .account import Account
from .trading_strategies import *



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

    def __init__(self, configs: dict) -> None:

        self.configs = configs

        self.running = True

        account_name = configs["account"]
        
        
        self.set_account(account_name)

        trading_strategy_class: BaseTradingStrategy = getattr(
            trading_strategies, configs["trading_strategy"])
        

        self.trading_strategy = trading_strategy_class()

    
    def account_data_dir(self, account_name: str):
        return "data/" + account_name + ".json"
    
    def set_account(self, account_name):
        self.configs["account"] = account_name
        account_dir = self.account_data_dir(account_name)
        if osp.exists(account_dir):
            with open(account_dir, 'r') as data_file:
                account_data = json.loads(data_file.read())
        else:
            account_data = dict()
        self.account = Account(account_name, account_data)
        

    def save_account_data(self):
        with open(self.account_data_dir(self.account.account_name), 
                  "w") as data_file:
            data_file.write(json.dumps(self.account.in_dict, indent=4))

    def save_setting(self, config_dir):
        with open(config_dir, 'w') as config_file:
            config_file.write(json.dumps(self.configs, indent=4))


    def proc(self) -> bool:
        pass



class BaseMenuInterface (Interface):
    '''
    An base menu driven interface

    Additional Fields:
        auto_trade      -   bool
        menus           -   dict(Label, Menu)
    '''

    def __init__(self, configs: dict) -> None:
        
        super().__init__(configs)

        self.auto_trade = configs["auto_trade"]

        self.set_menus()

    
    def set_menus(self):
        
        self.menus = dict()


        main_menu = {"func": self.main_handle,
                    "cmds": ["help", "details",
                             "set",
                             "transfer", "setbudget",
                             "addstock", "buy", "sell",
                             "undo", "remove",
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
            self.transfer, "tf|transfer", "transfer fund to/from budget"]
        main_menu_cmd_handler["tf"] = main_menu_cmd_handler["transfer"]

        main_menu_cmd_handler["setbudget"] = [
            self.set_budget, "sb|setbudget", "set budget"]
        main_menu_cmd_handler["sb"] = main_menu_cmd_handler["setbudget"]

        
        main_menu_cmd_handler["addstock"] = [
            self.add_stock, "as|addstock", "add a stock"]
        main_menu_cmd_handler["as"] = main_menu_cmd_handler["addstock"]

        main_menu_cmd_handler["buy"] = [
            self.buy_stock, "b|buy", "buy stocks"]
        main_menu_cmd_handler["b"] = main_menu_cmd_handler["buy"]

        main_menu_cmd_handler["sell"] = [
            self.sell_stock, "s|sell", "sell stocks"]
        main_menu_cmd_handler["s"] = main_menu_cmd_handler["sell"]

        main_menu_cmd_handler["undo"] = [
            self.undo_trade, "undo", "undo a trade"]

        main_menu_cmd_handler["remove"] = [
            self.remove_stock, "r|remove", "remove a stock from the bundle"]
        main_menu_cmd_handler["r"] = main_menu_cmd_handler["remove"]


        main_menu_cmd_handler["exit"] = [
            self.exit, "exit", "exit the program"]


        setting = {"func": self.setting_handle,
                   "cmds": ["help", "details",
                            "switchaccount", "setstrategy", "setautotrade",
                            "back"],
                   "cmd_handler": dict()}
        
        self.menus["setting"] = setting
        setting_cmd_handler = setting["cmd_handler"]

        setting_cmd_handler["help"] = [
            self.show_hints, "help", "view command instructions"]
        
        setting_cmd_handler["details"] = [
            self.show_config_details, "d|details", "view config details"]
        setting_cmd_handler["d"] = setting_cmd_handler["details"]
        
        setting_cmd_handler["switchaccount"] = [
            self.switch_account, "sa|switchaccount", "switch account"]
        setting_cmd_handler["sa"] = setting_cmd_handler["switchaccount"]

        setting_cmd_handler["setstrategy"] = [
            self.set_strategy, "ss|setstrategy", "change strategy"]
        setting_cmd_handler["ss"] = setting_cmd_handler["setstrategy"]

        setting_cmd_handler["setautotrade"] = [
            self.set_auto_trade, "sat|setautotrade", "set autotrade"]
        setting_cmd_handler["sat"] = setting_cmd_handler["setautotrade"]

        setting_cmd_handler["back"] = [
            self.to_main, "back", "go back to the main page"]
        

        self.cur_location = main_menu


    def proc(self):
        self.cur_location["func"]()
        return self.running

    

    def main_handle(self) -> None:
        print("You are at the main menu.")
        print("Type 'help' to see available comands.")
    
        cmd = self.get_str()
        print()
        self.cur_location["cmd_handler"].get(cmd, [self.cmd_err])[0]()
        print()

    
    def setting_handle(self) -> None:
        print("You are at the setting.")
        print("Type 'help' to see available comands.")

        cmd = self.get_str()
        print()
        self.cur_location["cmd_handler"].get(cmd, [self.cmd_err])[0]()
        print()


    def show_hints(self):
        print("Avaliable Comands:")
        for cmd in self.cur_location["cmds"]:
            cmd = self.cur_location["cmd_handler"][cmd]
            print(" "*4, '{0: <25}'.format("[" + cmd[1] + "]"),
                cmd[2], sep = "")
    
            
    def show_account_details(self):
        print(self.account)

    def show_config_details(self):
        print(self.configs)

    
    def to_main(self):
        self.cur_location = self.menus["main_menu"]

    def to_setting(self):
        self.cur_location = self.menus["setting"]


    def switch_account(self):
        self.save_account_data()
        account_name = self.get_str("Account name: ")
        self.set_account(account_name)
        self.configs["account"] = account_name
        print("Switch to", account_name)

    
    def set_strategy(self):
        nstrategy = self.get_str("Strategy name")
        if nstrategy not in trading_strategies_set:
            print("Strategy not avaiable. Nothing is done.")
        else:
            self.configs["trading_strategy"] = nstrategy
            print("Using", nstrategy)
    

    def set_auto_trade(self):
        self.auto_trade = not self.auto_trade
        self.configs["auto_trade"] = self.auto_trade
        print("set auto_trade to", self.auto_trade)


    def add_stock(self):
        stock_label = self.get_str("Label of the stock: ")
        if self.account.contains_stock(stock_label):
            print("Stock", stock_label, "is already in the bundle.")
        else:
            self.account.add_stock(stock_label)


    def buy_stock(self):
        stock_label, units, value, price = self.get_trade_info()
        if not self.account.contains_stock(stock_label):
            self.account.add_stock(stock_label)
        
        stock = self.account.bundle[stock_label]
        self.trade(stock, abs(units), abs(value), price)

        
    def sell_stock(self):
        stock_label, units, value, price = self.get_trade_info()
        if not self.account.contains_stock(stock_label):
            print("Stock is not contained in the bundle. Nothing is done.")
            return

        stock = self.account.bundle[stock_label]
        self.trade(stock, -abs(units), -abs(value), price)

    def undo_trade(self):
        stock_label = self.get_str("Label of the stock: ")
        if not self.account.contains_stock(stock_label):
            print("Stock is not contained in the bundle. Nothing is done.")
            return
        stock = self.account.bundle[stock_label]
        self.account.budget += stock.undo_change()
        


    def remove_stock(self):
        stock_label = self.get_str("Label of the stock: ")
        if not self.account.contains_stock(stock_label):
            print("Your bundle doesn't contain ", stock_label,
                  ", Nothing is done.", sep= "")
        else:
            self.account.bundle.pop(stock_label)


    def transfer(self):
        amount = self.get_num("Amount: ")
        self.account.budget += amount

    def set_budget(self):
        amount = self.get_num("Amount: ")
        self.account.budget = amount


    def get_trade_info(self) -> tuple[str, float, float, float]:
        stock_label = self.get_str("Label of the stock: ")
        units = abs(self.get_num("Units: "))
        value = abs(self.get_num("Value: "))
        price = self.get_num("Price: ")
        return stock_label, units, value, price
    
    def trade(self, stock: Stock, units, value, price) -> None:
        if not stock.varify_trade(units, value, self.account.budget):
            print("Invalid attempt to trade. Nothing is done.")
        else:
            stock.update_change(units, value, price)
            self.account.budget -= value        


    def exit(self):
        self.running = False
    
    def cmd_err(self):
        print("Invalid command. Nothing is done.")


    def get_str(self, display: str = "") -> str:
        return input(display)
    
    def get_num(self, display: str = "", num: type = float) -> float|int:
        def get():
            try:
                n = num(input(display))
            except ValueError:
                print("ValueError: please enter a number")
                return None
            return n
        
        n = None
        while n == None:
            n = get()
        return n