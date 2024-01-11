import pandas as pd
import matplotlib.pyplot as plt
import statistics



class StockStatistics:
    '''
    A class object handles statistics of stock data
    '''
    def __init__(self, stock_data: dict) -> None:
        self.stock_data         = stock_data
        self.daily_data         = pd.DataFrame(stock_data['daily'])
        numeric_columns_names   = set(self.daily_data.columns)
        numeric_columns_names.remove('date')
        for name in numeric_columns_names:
            self.daily_data[name] = pd.to_numeric(self.daily_data[name])
        self.daily_data['datetime'] = pd.to_datetime(self.daily_data['date'])
        self.get_functions      = {
            'variate':  self.get_variate,
            'mean':     self.get_mean,
            'min':      self.get_min,
            'max':      self.get_max
        } 

    
    @property
    def in_dict(self):
        return self.stock_data


    def get(self, statistics: str,
                    beg: str|None = None, end: str|None = None
                ) -> list|float|int|str:
        '''
        Gets data on a certain date or a list of data in a period
        '''
        data = self.daily_data
        beg = self.get_index(data, beg, 0)
        end = self.get_index(data, end, -1) + 1
        
        if statistics not in self.get_functions.keys():
            return self.get_functions['variate'](statistics, beg, end)
        else:
            return self.get_functions[statistics](beg, end)
    

    def get_index(self, data: pd.DataFrame, date:str|None, default = 0) -> int:
        '''
        Gets index by date;
            returns default index if date is not in the dataframe
        '''
        if date is None or len(data.loc[data['date'] == date]) == 0:
            if default < 0:
                default += len(data)
                default = max(0, default)
            idx = default
        else:
            idx = data.loc[data['date'] == date].index[0]
        return idx
    
    def get_variate(
            self, variate_name: str, beg: int, end: int|None = None
            ) -> list|float|int|str:
        '''
        Gets variates on by index or range 
        '''
        beg = self.get_index(self.daily_data, None, beg)
        if end is None:
            return self.daily_data[variate_name][beg]
        else:
            end = self.get_index(self.daily_data, None, end)
            return list(self.daily_data[variate_name][beg:end+1])

    def get_mean(self, beg: int, end: int):
        return statistics.mean(self.get_variate(
            'close', beg = beg, end = end))

    def get_min(self, beg: int, end: int):
        return min(self.get_variate(
            'low', beg = beg, end = end))


    def get_max(self, beg: int, end: int):
        return max(self.get_variate(
            'high', beg = beg, end = end))
    


    def plot_attributes(self, attributes):
        self.daily_data.plot('datetime', attributes)
        plt.show()