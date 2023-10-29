import json
from . import trading_strategies
from . import interface
from src.interface import Interface
from src.account import Account
from src.trading_strategies import *


class Runner:

    def __init__(self, config_dir: str) -> None:
        self.config_dir = config_dir
        
        with open(config_dir, 'r') as config_file:
            config = json.loads(config_file.read())

        interface_class = getattr(
            interface, config["interface"])
        self.interface: Interface = interface_class(config)

    def save_data(self) -> None:
        self.interface.save_account_data()
        self.interface.save_setting(self.config_dir)


    def run(self) -> None:
        while self.interface.proc():
            pass
    


