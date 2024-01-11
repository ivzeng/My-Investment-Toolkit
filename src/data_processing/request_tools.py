import requests
import json
import pandas as pd
import time


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
            beg: str = '0', end: str = '20500101',
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
        detials = data["klines"]
        daily = dict()
        for f_tag in fields:
            daily[f_tag] = list()
        for d_str in detials:
            day = d_str.split(',')
            for i in range(len(day)):
                daily[fields[i]].append(day[i])
        data.pop("klines")
        data["daily"] = daily

        return data, pd.DataFrame(daily)
    



