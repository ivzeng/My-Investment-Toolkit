from ..data_processing import trading_strategies
from ..objects.account import Account
from ..objects.current import Current
from ..data_processing.stock_statistics import StockStatistics
from ..data_processing.trading_strategies import *
from ..data_processing.my_json import MyJson
from ..data_processing.request_tools import *
from ..io.io import *
from ..helper.display import *
from ..helper.directory import *
import matplotlib.pyplot as plt
#from ..objects.stock import Stock





# Type def:
#   Menu    -   {'func': Func, 'cmds': list[str], 'cmd_handler': list[Cmd]}
#   Cmd     -   [Func, str, str]
#   Func    -   Callable


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
        
        self.set_trading_strategy(trading_strategy)

        self.set_account(account_name)

        self.load_stock_info()

        self.load_stock_data()


    
    def set_trading_strategy(self, strategy_name:str):
        self.configs['trading_strategy']    = strategy_name
        trading_strategy_class: BaseTradingStrategy = getattr(
            trading_strategies, strategy_name)
        self.trading_strategy: BaseTradingStrategy  = trading_strategy_class(
            self.my_json)
    
    def set_account(self, account_name):
        '''
        Loads account‘s data
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



class BaseMenuInterface (Interface):
    '''
    An base menu driven interface

    Fields:
        io              : ConsoleIO
        menus           : dict(Label, Menu)
    '''

    def __init__(self, configs: dict, my_json: MyJson) -> None:
        self.io = ConsoleIO()
        super().__init__(configs, my_json)
        self.set_menus()

    
    def set_menus(self):
        '''
        Sets menus' details and handlers
        '''
        
        self.menus = dict()


        main_menu = {'func': self.main_handle,
                    'cmds': ['help', 'details',
                             'set',
                             'save',
                             'transfer', 'setbudget',
                             'add', 'trade', 'undo', 'remove',
                             'setstock', 'updatestocks', 'updatestock',
                             'plot',
                             'suggestion', 'simulate',
                             'exit'],
                      'cmd_handler': dict()}
        
        self.menus['main_menu'] = main_menu
        main_menu_cmd_handler = main_menu['cmd_handler']


        main_menu_cmd_handler['help'] = [
            self.show_hints, 'help', 'view command instructions']
        
        main_menu_cmd_handler['details'] = [
            self.show_account_details, 'd|details', 'view account details']
        main_menu_cmd_handler['d'] = main_menu_cmd_handler['details']
        
        main_menu_cmd_handler['set'] = [
            self.to_setting, 'set|configs', 'go to the setting']
        main_menu_cmd_handler['configs'] = main_menu_cmd_handler['set']

        main_menu_cmd_handler['save'] = [
            self.save, 'save', 'save data']

        main_menu_cmd_handler['transfer'] = [
            self.transfer, 'tf|transfer', 'transfer to/from budget']
        main_menu_cmd_handler['tf'] = main_menu_cmd_handler['transfer']

        main_menu_cmd_handler['setbudget'] = [
            self.set_budget, 'sb|setbudget', 'set budget']
        main_menu_cmd_handler['sb'] = main_menu_cmd_handler['setbudget']

        
        main_menu_cmd_handler['add'] = [
            self.add_stock, 'a|addstock', 'add a stock to the bundle']
        main_menu_cmd_handler['a'] = main_menu_cmd_handler['add']

        main_menu_cmd_handler['trade'] = [
            self.update_trade, 't|trade', 'update new trade']
        main_menu_cmd_handler['t'] = main_menu_cmd_handler['trade']

        main_menu_cmd_handler['undo'] = [
            self.undo_trade, 'undo', 'undo a trade']
        
        main_menu_cmd_handler['remove'] = [
            self.remove_stock, 'r|remove', 'remove a stock from the bundle']
        main_menu_cmd_handler['r'] = main_menu_cmd_handler['remove']
        

        main_menu_cmd_handler['setstock'] = [
            self.set_stock_info,
            'ss|setstock', 'set stock\'s general information']
        main_menu_cmd_handler['ss'] = main_menu_cmd_handler['setstock']

        main_menu_cmd_handler['updatestocks'] = [
            self.update_stocks_data, 
            'uss|updatestocks', 'update all stocks\' historical data']
        main_menu_cmd_handler['uss'] = main_menu_cmd_handler['updatestocks']

        main_menu_cmd_handler['updatestock'] = [
            self.update_stock_data, 
            'us|updatestock', 'update single stock\'s historical data']
        main_menu_cmd_handler['us'] = main_menu_cmd_handler['updatestock']


        main_menu_cmd_handler['plot'] = [
            self.plot, 
            'plot', 'plot single stock\'s price']


        main_menu_cmd_handler['suggestion'] = [
            self.apply_strategy, 'suggestion', 'get suggestion']
        
        main_menu_cmd_handler['simulate'] = [
            self.trade_simulation, 'simulate', 'simulate trading with the strategy']

        main_menu_cmd_handler['exit'] = [
            self.exit, 'exit', 'exit the program']


        setting = {'func': self.setting_handle,
                   'cmds': ['help', 'details',
                            'account', 'strategy',
                            'back'],
                   'cmd_handler': dict()}
        
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

        setting_cmd_handler['strategy'] = [
            self.switch_strategy, 's|strategy', 'change strategy']
        setting_cmd_handler['s'] = setting_cmd_handler['strategy']

        setting_cmd_handler['back'] = [
            self.to_main, 'back', 'go back to the main page']
        

        self.cur_location = main_menu


    def proc(self):
        '''
        Processes one step
        '''
        self.cur_location['func']()
        return self.running

    

    def main_handle(self) -> None:
        '''
        Reads cmds (main); prints error message if the cmd is invalid
        '''
        self.basis_handle('main menu')

    
    def setting_handle(self) -> None:
        '''
        Reads cmds (setting); prints error message if the cmd is invalid
        '''
        self.basis_handle('setting')
    
    def basis_handle(self, location: str) -> None:
        self.message('[' + location + ']')
        self.hint('Type \'help\' to see available comands.')

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


    def add_stock(self):
        '''
        Adds a stock into the account\'s bundle
        '''
        stock_label = self.get_stock_lable()
        if self.account.contains_stock(stock_label):
            self.hint('Stock'+stock_label+'is already in the bundle.')
        else:
            self.account.add_stock(stock_label)


    def update_trade(self, 
                     stock_label: str = None,
                     date: str = None,
                     strategy_name: bool = None) -> None:
        '''
        Updates a trade if the trade is valid; does nothing otherwise
        '''
        if stock_label is None:
            stock_label = self.get_stock_lable()
        units       = self.get_units()
        if units is None:
            self.warning('Input is not an integer. Nothing is done.')
            return
        unit_price  = self.get_price()
        if unit_price is None:
            self.warning('Input is not a number. Nothing is done.')
            return
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

    
    
    def undo_trade(self):
        '''
        attempts to undo a trade
        '''
        stock_label = self.get_stock_lable()
        if not self.account.contains_stock(stock_label):
            self.warning('Stock is not in the bundle. Nothing is done.')
            return
        
        stock = self.account.get_stock(stock_label)
        amount_received = stock.undo_change()
        if amount_received == None:
            self.warning('There was no trading on this stock. Nothing is done.')
            return

        self.account.budget += amount_received


    def remove_stock(self):
        '''
        Removes stock from the bundle
        '''
        stock_label = self.get_stock_lable()
        if not self.account.contains_stock(stock_label):
            self.warning(f'Your bundle does not contain {stock_label}, Nothing is done.')
        elif self.account.is_holding(stock_label):
            self.warning(f'Your account is still holding {stock_label}, nothing is done.')
        else:
            self.account.remove_stock(stock_label)


    def set_stock_info(self, stock_label = None):
        '''
        Sets stock information
        '''
        if stock_label is None:
            stock_label = self.get_stock_lable()
        else:
            self.message(f'Setting information for [{stock_label}]:')
        stock_market, stock_code = self.get_stock_info()
        self.stock_info[stock_label] = [stock_market, stock_code]



    def update_stocks_data(self) -> None:
        '''
        Requests or update data of all stocks in the account
        '''
        period = self.get_period()
        for stock_label in self.stock_info.keys():
            self.update_stock_data(period, stock_label)

    def update_stock_data(self,  period = None, stock_label = None):
        
        '''
        Requests or update stock data
        '''
        if period == None:
            beg, end = self.get_period()
        else:
            beg, end = period[0], period[1]

        if stock_label is None: 
            stock_label = self.get_stock_lable()
        if stock_label not in self.stock_info.keys():
            self.set_stock_info(stock_label)


        self.message(
            f'Attempting to query history for [{stock_label}: '+
            f'{self.stock_info[stock_label][0]}.{self.stock_info[stock_label][1]}]:')
        try:
            request_tool = self.get_request_tool(self.stock_info[stock_label][0])
            requested, daily = request_tool.request_daily(
                market  =   self.stock_info[stock_label][0],
                code    =   self.stock_info[stock_label][1],
                beg     =   beg,
                end     =   end
            )
        except:
            self.warning("Failed to obtain the data.")
            self.hint("Please check your internet, and verify your input")
            return

        self.message("Successfully obtained the data.")
        print(daily[:6])
        print('...')
        print(daily[-6:])

        self.stocks_statistics[stock_label] = StockStatistics(requested)
    

    def get_request_tool(self, market) -> BaseRequest:
        if market == '1' or market == '0':
            return CNRequest()
        return None
        

    def plot(self, stock_label = None):
        if stock_label == None:
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
                self.message(f'Suggested trade: {trade[-1]}')
                reply = self.get_input('Update trade? (N/n to reject)')
                if reply != 'n' or reply == 'N':
                    self.update_trade(
                        trade[0],
                        self.stocks_statistics[trade[0]].get(
                            'date', -1),
                        self.trading_strategy.class_name)
        

        self.message('Generating future suggestion ...')
        future_suggestions = self.trading_strategy.suggestions(
            self.stocks_statistics, self.account
        )
        for stock_label in future_suggestions.keys():
            self.show_suggestion(stock_label, future_suggestions[stock_label])

    
    def trade_simulation(self):
        beg, end = self.get_period()
        beg = f'{beg[:4]}-{beg[4:6]}-{beg[6:8]}'
        end = f'{end[:4]}-{end[4:6]}-{end[6:8]}'
        
        stocks = self.get_stock_bundle()
        self.message(f'Simulation with {self.trading_strategy.class_name} in period {beg} - {end}:')
        simulation_result = self.trading_strategy.simulation(self.stocks_statistics, stocks, beg, end)
        for hist in simulation_result['log']:
            print(hist)
        
        dates = simulation_result['date']
        for label in simulation_result['rate'].keys():
            plt.plot(dates, simulation_result['rate'][label], label=label)
        plt.legend(loc="upper left")
        plt.xticks(rotation=90)
        plt.show()
        



    def exit(self):
        self.running = False



    def switch_account(self):
        '''
        Saves current account's data and switch account 
        '''
        self.save_account_data()
        account_name = self.get_input('Account name: ')
        self.set_account(account_name)
        print('Switch to', account_name)

    def get_stock_bundle(self):
        stocks = self.get_input('Please enter a list of stock labels separated by spaces: ').split(' ')
        return [stock for stock in stocks if stock in self.stocks_statistics.keys()]


    
    def switch_strategy(self):
        '''
        Attempts to switch trading strategy
        '''
        nstrategy = self.get_input('Strategy name: ')
        if nstrategy not in trading_strategies_set:
            print('Strategy not avaiable.')
            print('Please input one of the following:', trading_strategies_set)
            print('Nothing is done.')
        else:
            self.set_trading_strategy(nstrategy)
            print('Using', nstrategy, 'strategy.')
    

    def set_auto_trade(self):
        self.auto_trade = not self.auto_trade
        self.configs['auto_trade'] = self.auto_trade
        print('set auto_trade to', self.auto_trade)


        
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
        
        self.io.output_message(
            '[' + stock_label + ']:\n  '\
            + '\n  '.join([suggestion[0] for suggestion in suggestions]))
    
    
    def message(self, content, type = None):
        self.io.output_message(content, type)

    


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
    

