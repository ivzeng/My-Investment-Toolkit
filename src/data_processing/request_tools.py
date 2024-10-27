import requests
import json
import pandas as pd
import time
import datetime
import yfinance as yf
from yahoofinancials import YahooFinancials


class BaseRequest:
    def __init__(self) -> None:
        '''
        Class handles stock data requests
        '''
        pass

    def request_daily (
            self, market: str, code: str, beg: str, end: str, fields: list
        ) -> dict:
        '''
        Returns a dictionary that contains stock's information 
            (listed in fields) for each day in date range [beg, end]
        '''
        pass

class CNRequest (BaseRequest):

    def __init__(self) -> None:
        super().__init__()

        # a map converting field names to api's parameters
        self.fields_map = {
            "date":"f51", "open":"f52", "close":"f53",
            "high":"f54", "low":"f55", "amount":"f56", "volume":"f57", 
            "range%":"f58", "change%":"f59", "change":"f60",
            "turnover%":"f61"
        }


    def request_daily(
            self, market: str, code: str,
            beg: str = '19000101', end: str = '20500101',
            fields: list = [
                    "date", "open", "close", "high", "low", 
                    "amount", "volume", 
                    "range%", "change%", "change",
                    "turnover%"]
        ) -> tuple[dict, pd.DataFrame]:
        '''
        Queries everyday data form internet; return data in forms of
            dictionary and dataframe
        '''

        def get_params():
            return {
                    "secid": market + "." + code,
                    "ut": "fa5fd1943c7b386f172d6893dbfba10b",
                    "fields1": "f1,f2,f3",
                    "fields2": ",".join(self.fields_map[tag] for tag in fields),
                    "klt": "101",
                    "beg": beg,
                    "end": end,
                    "fqt": "1",
                    "lmt": "210",
                    "cb": "quote_jp3"
                }
        
        def get_json_component(text:str) -> str:
            l, r = 0, len(text)
            while text[l] != '{':
                l += 1
                if l == len(text):
                    return ''
            while text[r-1] != '}':
                r -= 1
                if r == 0:
                    return ''
            return text[l:r]
        
        # requests data
        api_url = 'https://push2his.eastmoney.com/api/qt/stock/kline/get'
        api_params = get_params()
        get = requests.get(api_url, api_params)

        # processes data
        data = json.loads(get_json_component(get.text))["data"]
        details = data["klines"]
        daily = dict()
        for f_tag in fields:
            daily[f_tag] = [None for _ in range(len(details))]
        for j, d_str in enumerate(details):
            daily_data = d_str.split(',')
            for i in range(len(daily_data)):
                daily[fields[i]][j] = daily_data[i]
        data.pop("klines")
        data["daily"] = daily

        return data, pd.DataFrame(daily)
    




class USRequest(BaseRequest):
    def __init__(self) -> None:
        """Class handles stock data requests"""
        super().__init__()


    def request_daily(
            self, market: str, code: str,
            beg: str = '19000101', end: str = '20500101',
            fields: list = [
                    "open", "close", "high", "low", 
                    "amount", "volume", 
                    "range%", "change%", "change",
                    "turnover%"]
        ) -> tuple[dict, pd.DataFrame]:
        ticker = f'{code}'

        beg = f'{beg[:4]}-{beg[4:6]}-{beg[6:]}'
        end = f'{end[:4]}-{end[4:6]}-{end[6:]}'

        stock = yf.Ticker(ticker)
        daily = stock.history(start=beg, end=end)
        daily.columns = [col.lower() for col in daily.columns]
        
        if 'range%' in fields:
            daily['range%'] = ((daily['high'] - daily['low']) / daily['low']) * 100
        if 'change%' in fields:
            daily['change%'] = daily['close'].pct_change() * 100
        if 'change' in fields:
            daily['change'] = daily['close'].diff()
        if 'turnover%' in fields:
            shares_outstanding = stock.info['sharesOutstanding']
            daily['turnover%'] = (daily['volume'] / shares_outstanding) * 100
        if 'amount' in fields:
            daily['amount'] = daily['close']*daily['volume']
        daily = daily.fillna(0)
        
        output = {"market": market, "code": code, "daily": dict()}
        output['daily']['date'] = [str(d)[:10] for d in daily.index]

        for field in fields:
            output['daily'][field] = [str(d) for d in daily[field]]
        return output, daily
        

if __name__ == "__main__":
    '''
    request_tool = CNRequest()
    data, df = request_tool.request_daily(market='1', code='000001', beg='20231001', end='20231010', fields=['open', 'close', 'high', 'low', 'range%', 'change%', 'change', 'turnover%'])
    print(data)
    '''
    request_tool = USRequest()
    data, df = request_tool.request_daily(market='us', code='aapl', beg='20241001', end='20501030')
    print(df.columns)
    print(data)
    #'''
