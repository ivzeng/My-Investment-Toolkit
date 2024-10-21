from ..data_processing import trading_strategies
from ..objects.account import Account
from ..objects.current import Current
from ..data_processing.stock_statistics import StockStatistics
from ..data_processing.trading_strategies import *
from ..data_processing.my_json import MyJson
from ..data_processing.request_tools import *
from ..io.io import *
from ..io import notifier
from ..io.notifier import *

from ..helper.display import *
from ..helper.directory import *
from ..helper.type import *

import matplotlib.pyplot as plt
import threading
import time

import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox

#from ..objects.stock import Stock





# mtype def:
#   Menu    -   {'func': Func, 'cmds': list[str], 'cmd_handler': list[Cmd]}
#   Cmd     -   [Func, str, str]
#   Func    -   Callable

interface_set = {"BaseMenuUI", "MenuGUI"}


class Interface:
    '''
    An object that handles processes

    Fields:
        my_json             : MyJson
        configs             : dict
        running             : bool
        account_name        : str
        trading_straregy    : BaseTradingStrategy
        account             : Account
        stock_info          : dict[str, list]
        stocks_statistics   : dict[str, StockStatistics]
    
    Functions:
        set_trading_strategy
        set_account
        load_stock_info
        load_stock_data
        save
        save_account_data
        save_setting
        save_stock_info
        save_stock_data

    '''

    def __init__(self, configs: dict, my_json: MyJson) -> None:

        '''
        Initialize account data and tranding strategy
        '''

        self.my_json: MyJson    = my_json

        self.configs: dict      = configs

        self.running: bool      = True

        account_name: str       = self.configs['account']

        trading_strategy = self.configs['trading_strategy']

        self.set_notifier(self.configs['notifier'])
        
        self.set_trading_strategy(trading_strategy)

        self.set_account(account_name)

        self.load_stock_info()

        self.load_stock_data()

        self.auto = self.configs['auto']
        self.auto_sep = self.configs['auto_sep']


    def set_notifier(self, notifier_name:str):
        self.configs['notifier']    = notifier_name
        notifier_class: BaseNotifier = getattr(notifier, notifier_name)
        self.notifier: BaseNotifier  = notifier_class()

    
    def set_trading_strategy(self, strategy_name:str):
        self.configs['trading_strategy']    = strategy_name
        trading_strategy_class: BaseTradingStrategy = getattr(
            trading_strategies, strategy_name)
        self.trading_strategy: BaseTradingStrategy  = trading_strategy_class(
            self.my_json)
    
    def set_account(self, account_name):
        '''
        Loads account's data
        '''
        self.configs['account'] = account_name
        account_dir = account_data_dir(account_name)
        account_data = self.my_json.load(account_dir)
        self.account: Account   = Account(account_name, account_data)


    def load_stock_info(self):
        '''
        Loads the stocks' general information
        '''
        stock_info = stock_data_dir('info')
        self.stock_info: dict = self.my_json.load(stock_info)

    def load_stock_data(self):
        self.stocks_statistics: dict[str, StockStatistics] = dict()
        for stock_label in self.stock_info.keys():
            stock_data_d = stock_data_dir(stock_label)
            if osp.exists(stock_data_d):
                stock_data = self.my_json.load(stock_data_d)
                self.stocks_statistics[stock_label] = StockStatistics(stock_data)
    
    def save(self, config_dir = None):
        self.save_account_data()
        if not config_dir is None:
            self.save_setting(config_dir)
        self.save_stock_info()
        self.save_stock_data()
        

    def save_account_data(self):
        account_dir = account_data_dir(self.account.account_name)
        self.my_json.write(account_dir, self.account.in_dict)

    
    def save_setting(self, config_dir):
        self.my_json.write(config_dir, self.configs)

    def save_stock_info(self):
        stock_info_dir = stock_data_dir('info')
        self.my_json.write(stock_info_dir, self.stock_info)

    def save_stock_data(self):
        for stock_label in self.stocks_statistics.keys():
            stock_data_d = stock_data_dir(stock_label)
            self.my_json.write(
                stock_data_d, self.stocks_statistics[stock_label].in_dict)

    

    @property
    def current(self) -> Current:
        current = Current()
        for stock_label in self.stocks_statistics:
            current.set_price(
                stock_label,
                self.stocks_statistics[stock_label].get('close', beg = -1))
        return current



    def proc(self) -> bool:
        '''
        Processes one step
        '''
        pass



class BaseMenuUI (Interface):
    '''
    An base menu driven interface

    Fields:
        io              : ConsoleIO
        menus           : dict[Label, Menu]
        auto            : bool
    '''

    def __init__(self, configs: dict, my_json: MyJson) -> None:
        super().__init__(configs, my_json)
        self.io = ConsoleIO()
        self.set_menus()
        self.start_auto_update()


    
    def set_menus(self):
        '''
        Sets menus' details and handlers
        '''
        
        self.menus = dict()


        main_menu = {   'func': self.main_handle,
                        'location': 'main',
                        'cmds': [   'help', 'details',
                                    'set',
                                    'save',
                                    'transfer', 'setbudget',
                                    'add', 'trade', 'undo', 'remove',
                                    'setstock', 'updatestocks',
                                    'plot',
                                    'suggestion', 'simulate',
                                    'exit'
                                ],
                        'cmd_handler': dict()
                    }
        
        self.menus['main_menu'] = main_menu
        main_menu_cmd_handler = main_menu['cmd_handler']


        main_menu_cmd_handler['help'] = [
            self.show_hints, 'help', 'view command instructions']
        
        main_menu_cmd_handler['details'] = [
            self.show_account_details, 'details|d', 'view account details']
        main_menu_cmd_handler['d'] = main_menu_cmd_handler['details']
        
        main_menu_cmd_handler['set'] = [
            self.to_setting, 'set|configs', 'go to the setting']
        main_menu_cmd_handler['configs'] = main_menu_cmd_handler['set']

        main_menu_cmd_handler['save'] = [
            self.save, 'save', 'save data']

        main_menu_cmd_handler['transfer'] = [
            self.transfer, 'transfer|tf', 'transfer to/from budget']
        main_menu_cmd_handler['tf'] = main_menu_cmd_handler['transfer']

        main_menu_cmd_handler['setbudget'] = [
            self.set_budget, 'setbudget|sb', 'set budget']
        main_menu_cmd_handler['sb'] = main_menu_cmd_handler['setbudget']

        
        main_menu_cmd_handler['add'] = [
            self.add_stock, 'addstock|a', 'add a stock to the bundle']
        main_menu_cmd_handler['a'] = main_menu_cmd_handler['add']

        main_menu_cmd_handler['trade'] = [
            self.update_trade, 'trade|t', 'update new trade']
        main_menu_cmd_handler['t'] = main_menu_cmd_handler['trade']

        main_menu_cmd_handler['undo'] = [
            self.undo_trade, 'undo', 'undo a trade']
        
        main_menu_cmd_handler['remove'] = [
            self.remove_stock, 'remove|r', 'remove a stock from the bundle']
        main_menu_cmd_handler['r'] = main_menu_cmd_handler['remove']
        

        main_menu_cmd_handler['setstock'] = [
            self.set_stock_info,
            'setstock|ss', 'set stock\'s general information']
        main_menu_cmd_handler['ss'] = main_menu_cmd_handler['setstock']

        main_menu_cmd_handler['updatestocks'] = [
            self.update_stocks_data, 
            'updatestocks|uss', 'update all stocks\' historical data']
        main_menu_cmd_handler['uss'] = main_menu_cmd_handler['updatestocks']


        main_menu_cmd_handler['plot'] = [
            self.plot, 
            'plot', 'plot single stock\'s price']


        main_menu_cmd_handler['suggestion'] = [
            self.apply_strategy, 'suggestion', 'get suggestion']
        
        main_menu_cmd_handler['simulate'] = [
            self.trade_simulation, 'simulate', 'simulate trading with the strategy']

        main_menu_cmd_handler['exit'] = [
            self.exit, 'exit', 'exit the program']


        setting =   {   'func': self.setting_handle,
                        'location': 'setting',
                        'cmds': [   'help', 'details',
                                    'account', 'strategy', 'notifier', 'interface',
                                    'auto',
                                    'back'
                                ],
                        'cmd_handler': dict()
                    }
        
        self.menus['setting'] = setting
        setting_cmd_handler = setting['cmd_handler']

        setting_cmd_handler['help'] = [
            self.show_hints, 'help', 'view command instructions']
        
        setting_cmd_handler['details'] = [
            self.show_config_details, 'd|details', 'view configuations']
        setting_cmd_handler['d'] = setting_cmd_handler['details']
        
        setting_cmd_handler['account'] = [
            self.switch_account, 'a|account', 'switch account']
        setting_cmd_handler['a'] = setting_cmd_handler['account']

        setting_cmd_handler['notifier'] = [
            self.switch_notifier, 'n|notifier', 'change notifier']
        setting_cmd_handler['n'] = setting_cmd_handler['notifier']

        setting_cmd_handler['strategy'] = [
            self.switch_strategy, 's|strategy', 'change strategy']
        setting_cmd_handler['s'] = setting_cmd_handler['strategy']

        setting_cmd_handler['interface'] = [
            self.switch_interface, 'i|interface', 'change interface']
        setting_cmd_handler['i'] = setting_cmd_handler['interface']

        setting_cmd_handler['auto'] = [
            self.set_auto, 'auto', 'set auto update']

        setting_cmd_handler['back'] = [
            self.to_main, 'back', 'go back to the main page']
        
        self.cur_location = main_menu


    def proc(self):
        '''
        Processes one step
        '''
        self.cur_location['func']()
        return self.running
    

    def save(self, config_dir=None):
        super().save(config_dir)
        self.message("Saved account's, stock's, and config's data.")

    def start_auto_update(self):
        if self.auto:
            update_thread = threading.Thread(target=self.auto_update, args=(), daemon=True)
            update_thread.start()
    
    def auto_update(self):
        time.sleep(10)
        self.notifier.notify(f'Auto Update Started: Updating the stock data every {self.auto_sep} mimutes.')

        while self.auto:
            self.update_stocks_data('19000101', '20500101', verbose=False)
            self.message(f'[{datetime.datetime.now()}] Stock data updated!')
            triggered = self.trading_strategy.triggered_suggestions(
                self.stocks_statistics, self.account
            )
            if (len(triggered['sell']) != 0 or len(triggered['buy']) != 0):
                self.notifier.notify('Auto Update: Trading point triggered!', 'sound/alarm2.mp3')
            time.sleep(self.auto_sep*60)

    

    def main_handle(self) -> None:
        '''
        Reads cmds (main); prints error message if the cmd is invalid
        '''
        self.basis_handle('Main Menu')

    
    def setting_handle(self) -> None:
        '''
        Reads cmds (setting); prints error message if the cmd is invalid
        '''
        self.basis_handle('Setting')
    
    def basis_handle(self, location: str) -> None:
        self.message('[' + location + ']')
        self.hint('type \'help\' to see available comands.')

        cmd = self.get_input()
        self.io.line_break()
        self.cur_location['cmd_handler'].get(cmd, [self.cmd_err])[0]()
        self.io.line_break()


    def show_hints(self):
        '''
        Displays commands' instructions
        '''
        self.message('Avaliable Comands:')
        for cmd in self.cur_location['cmds']:
            cmd = self.cur_location['cmd_handler'][cmd]
            self.message(display('[' + cmd[1] + ']', 4, 25) + cmd[2])
    
            
    def show_account_details(self):
        self.message(self.account.details(self.current))


    def show_config_details(self):
        self.message(self.configs)



    def transfer(self):
        amount = self.get_num(
            'Amount: ', t = float, default = 0, exception = None, indents = 2,
            width = 18)
        if amount is None:
            self.warning('Input is not a number. Nothing is done.')
        else:
            self.account.budget += amount


    def set_budget(self):
        amount = self.get_num(
            'Amount: ', t = float, default = 0, exception = None, indents = 2,
            width = 18)
        if amount is None:
            self.warning('Input is not a number. Nothing is done.')
        else:
            self.account.budget = amount


    def add_stock(self, stock_label = None):
        '''
        Adds a stock into the account\'s bundle
        '''
        if stock_label is None:
            stock_label = self.get_stock_lable()
        if self.account.contains_stock(stock_label):
            self.hint(f'Stock [{stock_label}] is already in the bundle.')
        else:
            self.account.add_stock(stock_label)
            self.message(f'Stock [{stock_label}] have been added to your account bundle.')



    def update_trade(self, 
                     stock_label: str = None,
                     units: int = None, 
                     unit_price: float = None,
                     other_cost: float = None,
                     date: str = None,
                     strategy_name: bool = None) -> None:
        '''
        Updates a trade if the trade is valid; does nothing otherwise
        '''
        if stock_label is None:
            stock_label = self.get_stock_lable()
        if units is None:
            units       = self.get_units()
        if units is None:
            self.warning('Input is not an integer. Nothing is done.')
            return
        if unit_price is None:
            unit_price  = self.get_price()
        if unit_price is None:
            self.warning('Input is not a number. Nothing is done.')
            return
        if other_cost is None:
            other_cost  = self.get_cost()
        if other_cost is None:
            self.warning('Input is not a number. Nothing is done.')
            return
        if date is None:
            date        = self.get_date()
        
        if not self.account.contains_stock(stock_label):
            self.account.add_stock(stock_label)
        stock = self.account.get_stock(stock_label)
        

        if not self.account.valid_change(units, unit_price, other_cost)\
            or not stock.valid_change(units, unit_price):
            self.warning('Invalid trade. Nothing is done.')
        else:
            stock.update_change(
                units, unit_price, other_cost, date, strategy_name) 
            self.account.update_change(units, unit_price, other_cost)
            self.message(f'Updated trade: {units} {stock_label}, unit price: {unit_price}, other cost = {other_cost}.')


    
    
    def undo_trade(self, stock_label = None):
        '''
        attempts to undo a trade
        '''
        if stock_label is None:
            stock_label = self.get_stock_lable()
        if not self.account.contains_stock(stock_label):
            self.warning('Stock is not in the bundle. Nothing is done.')
            return
        
        stock = self.account.get_stock(stock_label)
        amount_received = stock.undo_change()
        if amount_received is None:
            self.warning('There was no trading on this stock. Nothing is done.')
            return

        self.account.budget += amount_received
        self.message(f'Undone trade for {stock_label}')


    def remove_stock(self, stock_label = None):
        '''
        Removes stock from the bundle
        '''
        
        if stock_label is None:
            stock_label = self.get_stock_lable()
        if not self.account.contains_stock(stock_label):
            self.warning(f'Your bundle does not contain {stock_label}, Nothing is done.')
        elif self.account.is_holding(stock_label):
            self.warning(f'Your account is still holding {stock_label}, nothing is done.')
        else:
            self.account.remove_stock(stock_label)


    def set_stock_info(self, stock_label = None, stock_market = None, stock_code = None):
        '''
        Sets stock information
        '''
        if stock_label is None:
            stock_label = self.get_stock_lable()
            stock_market, stock_code = self.get_stock_info()
        self.stock_info[stock_label] = [stock_market, stock_code]
        self.message(f'Set stock [{stock_label}: {stock_market}.{stock_code}].')




    def update_stocks_data(self, beg = None, end = None, verbose = True) -> None:
        '''
        Requests or update data of all stocks in the account
        '''
        if beg is None:
            beg, end = self.get_period()
        for stock_label in self.stock_info.keys():
            self.update_stock_data([beg, end], stock_label, verbose)


    def update_stock_data(self,  period, stock_label, verbose):
        
        '''
        Requests or update stock data
        '''

        try:
            request_tool = self.get_request_tool(self.stock_info[stock_label][0])
            requested, daily = request_tool.request_daily(
                market  =   self.stock_info[stock_label][0],
                code    =   self.stock_info[stock_label][1],
                beg     =   period[0],
                end     =   period[1]
            )
        except:
            self.warning("Failed to obtain the data.")
            self.hint("Please check your internet, and verify your input")
            return
        if verbose:
            self.message(f"Successfully updated the stock [{stock_label}: " +
                f"{self.stock_info[stock_label][0]}.{self.stock_info[stock_label][1]}]")

        self.stocks_statistics[stock_label] = StockStatistics(requested)
    

    def get_request_tool(self, market) -> BaseRequest:
        if market == '1' or market == '0':
            return CNRequest()
        return None
        

    def plot(self, stock_label = None):
        if stock_label is None:
            stock_label = self.get_stock_lable()
        
        if not stock_label in self.stocks_statistics.keys():
            self.warning('Stock data is not available. Failed to plot.')
            return 

        self.stocks_statistics[stock_label].plot_attributes(
            ['open', 'close'], stock_label)


    def apply_strategy(self):
        triggered = self.trading_strategy.triggered_suggestions(
            self.stocks_statistics, self.account
        )

        for trade_type in ['sell', 'buy']:
            for trade in triggered[trade_type]:
                self.message(f'Suggested trade [{trade[0]}]: {trade[-1]}')
                reply = self.get_input('Update trade? (N/n to reject)')
                if reply != 'n' or reply == 'N':
                    self.update_trade(
                        trade[0],
                        None, None, None,
                        self.stocks_statistics[trade[0]].get(
                            'date', -1),
                        self.trading_strategy.class_name)
        

        self.message('Generating future suggestion ...')
        future_suggestions = self.trading_strategy.suggestions(
            self.stocks_statistics, self.account
        )
        for stock_label in future_suggestions.keys():
            self.show_suggestion(stock_label, future_suggestions[stock_label])

    
    def trade_simulation(self, beg: str = None, end: str = None, bundle = None):
        if beg is None or end is None:
            beg, end = self.get_period()
        if beg == '' or not beg.isnumeric() or len(beg) != 8:
            beg = '19000101'
        
        if end == '' or not end.isnumeric() or len(end) != 8:
            end = '20500101'
        
        if bundle is None:
            stocks = self.get_stock_bundle()
        else:
            stocks = bundle.split()
        if (len(stocks) == 0):
            self.message('There is no stock in the bundle.')
            return
        
  
        beg = f'{beg[:4]}-{beg[4:6]}-{beg[6:8]}'
        end = f'{end[:4]}-{end[4:6]}-{end[6:8]}'
        
        self.message(f'Simulation with {self.trading_strategy.class_name} in period {beg} - {end}:')
        simulation_result = self.trading_strategy.simulation(self.stocks_statistics, stocks, beg, end)
        for hist in simulation_result['log']:
            self.message(hist)
        self.message(f"Trade count: {simulation_result['trade_counts']}")
        ori_value = simulation_result['value']['account'][0]
        cur_value = simulation_result['value']['account'][-1]
        cur_rate = simulation_result['rate']['account'][-1]
        self.message(f"Original value: {ori_value}")
        self.message(f"Current value: {cur_value} ({100*(cur_rate-1)})%")
        
        dates = simulation_result['date']
        for label in simulation_result['rate'].keys():
            plt.plot(dates, simulation_result['rate'][label], label=label)
        plt.legend(loc="upper left")
        plt.xticks(rotation=90)
        plt.show()
        



    def exit(self):
        self.running = False



    def switch_account(self, account_name = None):
        '''
        Saves current account's data and switch account 
        '''
        self.save_account_data()
        if account_name is None:
            account_name = self.get_input('Account name: ')
        self.set_account(account_name)
        self.message(f'Switch to [{account_name}]')

    def get_stock_bundle(self):
        stocks = self.get_input('Please enter a list of stock labels separated by spaces: ').split(' ')
        return [stock for stock in stocks if stock in self.stocks_statistics.keys()]


    def switch_notifier(self, nnotifier = None):
        '''
        Attempts to switch notifier
        '''
        if nnotifier is None:
            nnotifier = self.get_input('Notifier name: ')
        if nnotifier not in notifier_set:
            self.message('Notifier not avaiable.')
            self.message(f'Please input one of the following: {notifier_set}')
            self.message('Nothing is done.')
        else:
            self.set_notifier(nnotifier)
            self.message(f'Using notifier {nnotifier}.')

    
    def switch_strategy(self, nstrategy:str = None):
        '''
        Attempts to switch trading strategy
        '''
        if nstrategy is None:
            nstrategy = self.get_input('Strategy name: ')
        if nstrategy not in trading_strategies_set:
            self.message('Strategy not avaiable.')
            self.message(f'Please input one of the following: {trading_strategies_set}')
            self.message('Nothing is done.')
        else:
            self.set_trading_strategy(nstrategy)
            self.message(f'Using strategy {nstrategy}.')

    def switch_interface(self, ninterface: str = None):
        if ninterface is None:
            ninterface = self.get_input('Interface name: ')
        if ninterface not in interface_set:
            self.message('Notifier not avaiable.')
            self.message(f'Please input one of the following: {interface_set}')
            self.message('Nothing is done.')
        else:
            self.configs['interface'] = ninterface
            self.message(f'Using strategy {ninterface}. Please restart the program.')
    

    def set_auto(self):
        self.auto = not self.auto
        self.configs['auto'] = self.auto
        self.message(f'set auto to {self.auto}.')
        self.start_auto_update()


        
    def to_main(self):
        self.cur_location = self.menus['main_menu']

    def to_setting(self):
        self.cur_location = self.menus['setting']

    


    def cmd_err(self):
        self.io.output_message('Invalid command. Nothing is done.', 'Error')
    
    def warning(self, content):
        self.io.output_warning(content)

    def hint(self, content):
        self.io.output_hint(content)

    def show_suggestion(self, stock_label: str, suggestions: list):
        self.message(f"[{stock_label}]:\n  "+ '\n  '.join([suggestion[0] for suggestion in suggestions]))
    
    
    def message(self, content, mtype = None):
        self.io.output_message(content, mtype)

    


    def get_stock_lable(self) -> str:
        return self.get_input('Stock label: ', 2, 18)
    

    def get_units(self) -> int:
        return self.get_num(
            'Units: ', t = int, default = 0, exception = None, indents = 2,
            width = 18)
    
    def get_price(self) -> float:
        return self.get_num(
            'Price: ', t = float, default = 0, exception = None, indents = 2,
            width = 18)
    
    def get_cost(self) -> float:
        return self.get_num(
            'Other cost: ', t = float, default = 0, exception = None, indents = 2,
            width = 18)
    
    def get_date(self) -> float:
        return self.get_input(
            'Date: ', indents = 2, width = 18)
    

    def get_stock_info(self) -> tuple[str, str]:
    
        market  = self.get_input(
            "Martet (0: Shenzhen, 1: shanghai): ", indents = 2, width = 40)
        code    = self.get_input("Code:", indents = 2, width = 40)
        return market, code
        
    
    def get_period(self) -> tuple[str, str]:
        self.message("Please enter the period (empty input -> all):")

        beg = self.get_input("Begin date:", indents = 2, width = 18)
        if beg == '':
            beg = '19000101'
        while len(beg) != 8:
            self.hint("a date should be in form: yyyymmdd")
            beg = self.get_input("Begin date:", indents = 2, width = 18)

        end = self.get_input("End date:", indents = 2, width = 18)
        if end == '':
            end = '20500101'
        while len(beg) != 8:
            self.hint("a date should be in form: yyyymmdd")
            end = self.get_input("End date:", indents = 2, width = 18)
        return beg, end
        


    def get_input(self,
                  content: str = '', indents: int = 0, 
                  width: int = None, pos: str = '<') -> str:
        return self.io.input(content, indents, width, pos)
    

    def get_num(
            self, content: str = '', t: type = float, default = 0,
            exception = None ,indents: int = 0, width: int = None,
            pos: str = '<' ) -> float|int:
        return self.io.input_item(
            content, t = t, default = default, exception = exception,
            indents = indents, width = width, pos = pos)

















class MenuGUI(BaseMenuUI):
    '''
    A menu-based Graphical UI
    '''
    def __init__(self, configs: dict, my_json: MyJson) -> None:
        super().__init__(configs, my_json)
        self.root = tk.Tk()
        self.root.geometry('1000x650')
        self.root.title('My Investment Toolkit')
        self.root_components : dict[str, tk.Label|tk.Button|tk.Entry] = dict()
        self.temp_fn = None
        self.temp_components: list = []
        for c in range(20):
            self.root.grid_columnconfigure(c, minsize=80)
        
        self.root.protocol("WM_DELETE_WINDOW", self.exit)



    def set_menus(self):
        '''
        Sets menus' details and handlers
        '''
        super().set_menus()



    def proc(self):
        '''
        Processes one step
        '''
        self.cur_location['func']()
        self.root.mainloop()
        return False


    
    def basis_handle(self, location: str) -> None:
        for component in self.root_components.keys():
            self.hide(self.root_components[component])
        loc_label = self.set_component(tk.Label, 'location')
        loc_label.grid(row = 0, column=0, columnspan=3)
        self.set_text(loc_label, f'{location}')
        self.set_size(loc_label, width=24, height=2)

        for i, cmd in  enumerate(self.cur_location['cmds']):
            button_label = f"{self.cur_location['location']}_{cmd}"
            button = self.set_component(tk.Button, button_label)
            button.grid(row=i//3+1, column=i%3)
            self.set_text(button, cmd)
            self.set_size(button, width=8, height=2)
            self.set_button_fn(button, self.cur_location['cmd_handler'][cmd][0])

        
    def to_main(self):
        super().to_main()
        self.cur_location['func']()

    def to_setting(self):
        super().to_setting()
        self.cur_location['func']()


    def show_hints(self):
        '''
        Displays commands' instructions
        '''
        super().show_hints()
    
            
    def show_account_details(self):
        super().show_account_details()



    def show_config_details(self):
        super().show_config_details()




    def transfer(self, amount = None):
        if amount == None:
            self.temp_fn = self.transfer
            self.hide_temp()
            self.query_input('Amount:', '')
            self.submit_button()
        else:
            amount = convert_to(amount, float, default=0)
            if amount is None or self.account.budget+amount < 0:
                self.num_warning()
            else:
                self.account.budget += amount
                self.message(f'Transfer Complete!\nCurrent budget: {self.account.budget}')
                self.hide_temp()



        


    def set_budget(self, amount = None):
        if amount == None:
            self.hide_temp()
            self.temp_fn = self.set_budget
            self.query_input('Amount:', '')
            self.submit_button()
        else:
            amount = convert_to(amount, float, 0)
            if amount is None:
                self.num_warning()
            else:
                self.account.budget = amount
                self.message(f'Budget set!\nCurrent budget: {self.account.budget}')
                self.hide_temp()
                


    def add_stock(self, stock_label = None):
        if stock_label is None:
            self.hide_temp()
            self.temp_fn = self.add_stock
            self.query_input('Stock Label:', '')
            self.submit_button()
        else:
            super().add_stock(stock_label)
            self.hide_temp()



    def update_trade(self, 
                     stock_label: str = None,
                     units: int = None, 
                     unit_price: float = None,
                     cost: float = None,
                     date: str = None,
                     strategy_name: bool = None) -> None:

        if stock_label is None or units is None or unit_price is None or cost is None or date is None:
            self.hide_temp()
            self.temp_fn = self.update_trade
            self.query_input('Stock Label:', stock_label)
            self.query_input('Units:', units)
            self.query_input('Unit Price:', unit_price)
            self.query_input('Other Cost:', cost)
            self.query_input('Date:', date)
            self.query_input('Strategy:', self.trading_strategy.class_name)
            self.submit_button()
        else:
            units = convert_to(units, int)
            unit_price = convert_to(unit_price, float)
            cost = convert_to(cost, float, 0)
            if units is None or unit_price is None or cost is None:
                self.num_warning()
                return
            super().update_trade(stock_label, units, unit_price, cost, date, strategy_name)
            self.hide_temp()

            
    
    def undo_trade(self, stock_label = None):
        '''
        attempts to undo a trade
        '''
        if stock_label is None:
            self.hide_temp()
            self.temp_fn = self.undo_trade
            self.query_input('Stock Label:', '')
            self.submit_button()

        else:
            super().undo_trade(stock_label)
            self.hide_temp()



    def remove_stock(self, stock_label = None):
        '''
        Removes stock from the bundle
        '''
        if stock_label is None:
            self.hide_temp()
            self.temp_fn = self.remove_stock
            self.query_input('Stock Label:', '')
            self.submit_button()
        else:
            super().remove_stock(stock_label)
            self.hide_temp()


    def set_stock_info(self, stock_label = None, stock_market = None, stock_code = None):
        '''
        Sets stock information
        '''
        if stock_label is None:
            self.hide_temp()
            self.temp_fn = self.set_stock_info
            self.query_input('Stock Label:', '')
            self.query_input('Stock Market (0: sz, 1:sh):', '')
            self.query_input('Stock code:', '')
            self.submit_button()
        else:
            super().set_stock_info(stock_label, stock_market, stock_code)
            self.hide_temp()



    def update_stocks_data(self, beg = None, end = None, verbose = True) -> None:
        '''
        Requests or update data of all stocks in the account
        '''
        if beg is None:
            self.hide_temp()
            self.temp_fn = self.update_stocks_data
            self.query_input('Begin date:', 'yyyymmdd')
            self.query_input('End Date:', 'yyyymmdd')
            self.submit_button()
        else:
            super().update_stocks_data(beg, end, verbose)
            self.hide_temp()



    def update_stock_data(self,  period, stock_label, verbose):
        super().update_stock_data(period, stock_label, verbose)
        

    def plot(self, stock_label = None):
        
        if stock_label is None:
            self.hide_temp()
            self.temp_fn = self.plot
            self.query_input('Stock Label:', '')
            self.submit_button()
        else:
            super().plot(stock_label)
            



    def apply_strategy(self):
        
        triggered = self.trading_strategy.triggered_suggestions(
            self.stocks_statistics, self.account
        )

        for trade_type in ['sell', 'buy']:
            for trade in triggered[trade_type]:
                reply = messagebox.askquestion('Trade point triggered!', f'Suggested trade [{trade[0]}]: {trade[-1]}\nUpdate trade?')
                if reply == 'yes':
                    self.update_trade(
                        trade[0],
                        None, None, None,
                        self.stocks_statistics[trade[0]].get('date', -1),
                        self.trading_strategy.class_name)
        

        self.message('Generating future suggestion ...')
        future_suggestions = self.trading_strategy.suggestions(
            self.stocks_statistics, self.account
        )
        for stock_label in future_suggestions.keys():
            self.show_suggestion(stock_label, future_suggestions[stock_label])
        

    
    def trade_simulation(self, beg:str = None, end:str = None, bundle: str = None):
        if beg is None or end is None or bundle is None:
            self.hide_temp()
            self.temp_fn = self.trade_simulation
            self.query_input('Begin date (yyyymmdd):', beg)
            self.query_input('End Date (yyyymmdd):', end)
            self.query_input('Stock bundle (stock1 stock2 stock3 ...)', bundle)
            self.submit_button()
        else:
            super().trade_simulation(beg, end, bundle)
        



    def exit(self):
        self.running = False
        self.root.quit()



    def switch_account(self, account_name = None):
        '''
        Saves current account's data and switch account 
        '''
        if account_name is None:
            self.hide_temp()
            self.temp_fn = self.switch_account
            self.query_input('Account Name:')
            self.submit_button()
        else:
            super().switch_account(account_name)



    def switch_notifier(self, nnotifier = None):
        if nnotifier is None:
            self.hide_temp()
            self.temp_fn = self.switch_notifier
            self.query_input('Notifier Name:')
            self.submit_button()
        else:
            super().switch_notifier(nnotifier)

    
    def switch_strategy(self, nstrategy = None):
        if nstrategy is None:
            self.hide_temp()
            self.temp_fn = self.switch_strategy
            self.query_input('Strategy Name:')
            self.submit_button()
        else:
            super().switch_strategy(nstrategy)
    
    def switch_interface(self, ninterface = None):
        if ninterface is None:
            self.hide_temp()
            self.temp_fn = self.switch_interface
            self.query_input('Interface Name:')
            self.submit_button()
        else:
            super().switch_interface(ninterface)

    def set_auto(self):
        super().set_auto()
    


    def message(self, content = '', mtype = None):
        if self.running == False:
            super().message(content, mtype)
            return
        msg: tk.Text = self.set_component(scrolledtext.ScrolledText, 'msg1')
        self.set_size(msg, width=96, height=16)
        msg.config(wrap=tk.WORD)
        msg.grid(column=0, row = 10, rowspan=8, columnspan=9)
        if mtype is None:
            mtype = 'None'
        msg.tag_config('warning', background= 'yellow', foreground="red")
        msg.tag_config('hint', background= 'green', foreground="yellow")

        msg.insert(tk.END, f'{content}\n', mtype)

        clear_button: tk.Button = self.set_component(tk.Button, 'msg1_clear')
        self.set_size(clear_button, width=8, height=2)
        self.set_text(clear_button, 'clear')
        self.set_button_fn(clear_button, fn=lambda: self.clear_text(msg))
        clear_button.grid(column=9, row = 17, sticky='S')
    
    def warning(self, content):
        self.message(content, 'warning')
    
    def hint(self, content):
        self.message(content, 'hint')
    
    def num_warning(self):
        self.warning('Invalid amount. Please enter a number.')
    


    def query_input(self, content: str = '', hints = '') -> str:
        idx = len(self.temp_components)//2
        col = 4+(len(self.temp_components)//6)*3
        label = self.set_component(tk.Label, f'input_label_{content}')
        self.set_text(label, content)
        self.set_size(label, height=2)
        label.grid(row=(idx*2)%6, column=col, columnspan=3)

        entry = self.set_component(tk.Entry, f'input_entry_{content}')
        self.set_entry_text(entry, hints)
        self.set_size(entry, width=24)
        entry.grid(row=(idx*2+1)%6, column=col, columnspan=3)

        self.temp_components.append(label)
        self.temp_components.append(entry)

    def submit_button(self):
        row = 6
        col = 5

        button = self.set_component(tk.Button, f'submit')
        self.set_size(button, width=8, height=2)
        self.set_text(button, 'submit')
        self.set_button_fn(button, fn=lambda:
                           self.temp_fn(*[self.temp_components[i*2+1].get() 
                                          for i in range(len(self.temp_components)//2)]))
        button.grid(column=col, row = row, sticky='E')
        self.temp_components.append(button)




    def set_component(self, component: type[tk.Widget], label: str):
        if not label in self.root_components.keys():
            self.root_components[label] = component(self.root)
        return self.root_components[label]

    def set_text(self, component: tk.Widget, text: str):
        component.config(text=text)
    
    def set_entry_text(self, entry: tk.Entry, text: str = None):
        if text is None:
            text = ''
        entry.delete(0, tk.END)
        entry.insert(0, text)
    
    def clear_text(self, component: tk.Widget):
        component.delete('1.0', tk.END)


    
    def set_size(self,  component: tk.Widget,  width:int = None, height:int = None):
        component.config(width=width, height=height)


    def set_button_fn(self, button: tk.Button, fn: callable):
        button.config(command=fn)

    def hide(self, component: tk.Button|tk.Entry|tk.Label|tk.Text, condition: callable = None):
        if condition is None or condition(component):
            component.grid_forget()

    def hide_temp(self):
        for temp in self.temp_components:
            self.hide(temp)
        self.temp_components = []


    
