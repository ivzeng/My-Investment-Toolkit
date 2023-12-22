import json
from . import trading_strategies
from . import interface
from src.interface import Interface
from src.account import Account
from src.trading_strategies import *
from src.my_json import MyJson


class Runner:
    '''
    Program runner
    '''

    def __init__(self, config_dir: str, my_json: MyJson) -> None:
        '''
        Loads main configuation; creates interface class
        '''
        self.my_json = my_json
        self.config_dir = config_dir

        default_configs = {
            "interface": "BaseMenuInterface",
            "trading_strategy": "BaseTradingStrategy",
            "account": "my_account_0",
            "auto_trade": False,
            "strategy_configs": {
                "SimpleReweight": { "days": 50 }
            }
        }
        configs = my_json.load(config_dir, default_configs)
        interface_class = configs["interface"]
        interface_class = getattr(interface, interface_class)
        self.interface: Interface = interface_class(configs, self.my_json)



    def run(self) -> None:
        while self.interface.proc():
            pass
    

    
    def save_data(self) -> None:
        '''
        Save account data and configuation
        '''
        self.interface.save_account_data()
        self.interface.save_setting(self.config_dir)
        self.interface.save_current()
    


