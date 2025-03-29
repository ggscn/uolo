import requests
import urllib

class Tiingo:
    def __init__(self) -> None:
        self.api_token = 'tiingo'
        self.base_url = 'https://api.tiingo.com/tiingo/'

    def request(self, method, url, **kwargs):

        resp = requests.request(method, url, **kwargs)
        return resp

    def get_historical_prices(self, ticker, start_date, end_date, resample_freq='monthly'):
        url_params = urllib.parse.urlencode({
             'startDate':start_date, 
             'endDate': end_date, 
             'format':'json', 
             'resambleFreq':resample_freq,
             'token':self.api_token
        })
        url = '{}daily/{}/prices'.format(
            self.base_url,ticker)
        results = self.request(
            'GET', url, params=url_params).json()
        return results
        

class Company:
    def __init__(self, ticker) -> None:
        self.ticker = ticker

    

    