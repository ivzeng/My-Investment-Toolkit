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
                beg: str|int = None, end: str|int|None = None
                ) -> any:
        '''
        Gets data on a certain date or a list of data in a period
        '''
        data = self.daily_data
        beg = self.get_index(data, beg)
        end = self.get_index(data, end)
        
        if statistics not in self.get_functions.keys():
            return self.get_functions['variate'](statistics, beg, end)
        else:
            return self.get_functions[statistics](beg, end)
    

    def get_index(self, data: pd.DataFrame = None, timepoint:str|int = 0) -> int:
        '''
        Gets the index corresponded to the date timepoint if timepoint is the string;
        Gets the positive index if timepoint is an int;
        Return n-1 if index >= the number of rows in the database (n), and 0 if index < 0. 
        '''
        if data is None:
            data = self.daily_data
        if timepoint is None:
            return None
        if isinstance(timepoint, str):
            idx = len(data.loc[data['date'] < timepoint])
        else:
            if timepoint < 0:
                timepoint += len(data)
                timepoint = max(0, timepoint)
            idx = timepoint
        idx = min(data.shape[0]-1, idx)
        return idx
    
    def get_next_date(self, cur: str) -> str:
        next_date = self.get('date', self.get_index(None, cur)+1)
    
    def get_variate(
            self, variate_name: str, beg: int|None, end: int|None = None
            ) -> list|float|int|str:
        '''
        Gets variates on by index or range 
        '''
        if beg is None:
            return None
        if end is None:
            return self.daily_data[variate_name][beg]
        else:
            return list(self.daily_data[variate_name][beg:end+1])

    def get_mean(self, beg: int, end: int):
        return statistics.mean(self.get_variate(
            'close', beg = beg, end = end))

    def get_min(self, beg: int, end: int):
        stat = self.get_variate('low', beg = beg, end = end-1)
        stat.append(self.get('close', end-1))
        return min(stat)


    def get_max(self, beg: int, end: int):
        stat = self.get_variate('high', beg = beg, end = end-1)
        stat.append(self.get('close', end-1))
        return max(stat)
    


    def plot_attributes(self, attributes, title: str = '', begin = 0, end = -1):
        self.daily_data.plot('datetime', attributes)
        plt.title(title)
        plt.show()


if __name__ == "__main__":
    import my_json
    json = my_json.MyJson()
    data = json.load('./data/stock_data/a.json')
    ss = StockStatistics(data)
    print(ss.get_variate('date', 975))