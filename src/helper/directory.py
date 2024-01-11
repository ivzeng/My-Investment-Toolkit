def account_data_dir(account_name: str, file_type = '.json'):
    return "data/account_data/" + account_name + file_type

def stock_data_dir(file_name: str, file_type = '.json'):
    return  "data/stock_data/" + file_name + file_type

def strategy_data_dir(strategy_name: str, file_type = '.json'):
    return  "data/strategy_data/" + strategy_name + file_type