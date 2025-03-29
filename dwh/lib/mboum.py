import requests
import pandas as pd
try:
    from .utils import retry
except:
    from utils import retry
from datetime import datetime

class MBoumHistoryWeeklyResponse:
    def __init__(self, response, symbol) -> None:
        self.response = response
        self.symbol = symbol

    def get_week_number(self, date_int):
        date_object = self.clean_date(date_int)
        iso_week_number = date_object.isocalendar()[1]
        return iso_week_number
    
    def clean_date(self, date_string):
        return datetime.strptime(
            date_string, '%d-%m-%Y')
    
    def to_dict(self, cik=None):
        if 'error' in self.response:
            print(self.response, self.symbol)
            return []
        data = []
        for key, value in self.response['data'].items():
            data.append({
                'day_int': key,
                'symbol': self.symbol,
                'day_utc_int': value['date_utc'],
                'day': self.clean_date(value['date']),
                'volume': value['volume'],
                'open_price': value['open'],
                'close_price': value['close'],
                'adjusted_close_price': value.get('adjclose'),
                'low_price': value['low'],
                'high_price': value['high'],
                'iso_week_number': self.get_week_number(value['date']),
                'instrument_type': self.response['meta']['instrumentType'],
                'cik': cik
            })
        return data
    
class MBoumHistoryMonthlyResponse:
    def __init__(self, response, symbol) -> None:
        self.response = response
        self.symbol = symbol

    def get_month_number(self, date_int):
        date_object = self.clean_date(date_int)
        iso_week_number = date_object.month
        return iso_week_number
    
    def clean_date(self, date_int):
        return datetime.strptime(
            datetime.fromtimestamp(date_int).strftime('%Y-%m-%d'), '%Y-%m-%d')
    
    def process_response(self, cik=None):
        data = []
        for key, value in self.response['data'].items():
            data.append({
                'day_int': key,
                'symbol': self.symbol,
                'day_utc_int': value['date_utc'],
                'day': self.clean_date(value['date_utc']),
                'volume': value['volume'],
                'open_price': value['open'],
                'close_price': value['close'],
                'adjusted_close_price': value.get('adjclose'),
                'low_price': value['low'],
                'high_price': value['high'],
                'month': self.get_month_number(value['date_utc']),
                'instrument_type': self.response['meta']['instrumentType'],
                'cik': cik
            })
        df = pd.DataFrame(data)
        df['day'] = pd.to_datetime(df['day'])
        df = df[df['day'] < datetime.today().strftime('%Y-%m-01')]
        return df
    
    def to_dict(self, cik=None):
        if 'error' in self.response:
            print(self.response, self.symbol)
            return []
        return self.process_response(cik=cik).to_dict('records')


class MBoumHTTP:
    def __init__(self) -> None:
        self.apikey = 'mboumkey'
        self.base_url = 'https://mboum.com/api/v1'

    @retry(5,5)
    def request(self, url, params):
        params.update(apikey=self.apikey)

        response = requests.get(url, params=params)
        return response.json()
        
    def get_weekly_history(self, symbol):
        params = {
            'symbol': symbol,
            'interval': '1wk'
        }

        url = self.base_url + '/hi/history/'

        response = self.request(url, params)

        return MBoumHistoryWeeklyResponse(response, symbol)
    
    def get_monthly_history(self, symbol):
        params = {
            'symbol': symbol,
            'interval': '1mo',
            'range': '10y'
        }

        url = self.base_url + '/hi/history/'

        response = self.request(url, params)

        return MBoumHistoryMonthlyResponse(response, symbol)

    def get_balance_sheet(self, symbol):
        params = {
            'symbol': symbol
        }

        url = self.base_url + '/qu/quote/balance-sheet/'

        response = self.request(url, params)

        return response


print(MBoumHTTP().get_balance_sheet('AAPL'))