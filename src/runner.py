import json
from .interface import interface
from .interface.interface import Interface
from .objects.account import Account
from .data_processing.trading_strategies import *
from .data_processing.my_json import MyJson


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
            "account": "my_account_0"
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
        self.interface.save(self.config_dir)
    


