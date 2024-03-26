import requests
try:
    from .utils import retry
except:
    from utils import retry


class YrQuery:
    def __init__(self) -> None:
        self.user_agent = "PersonalWeatherTracker email"
        self.base_url = 'https://api.met.no/weatherapi'

    @retry(10,60)
    def issue_request(self, url, params):
        headers = {
            'User-Agent': self.user_agent
        }

        response = requests.get(
            url, headers=headers, params=params).json()
        return response

    def get_forecast(self, lat, lon):
        url = self.base_url + '/locationforecast/2.0/compact'
        params = {
            'lat': lat,
            'lon': lon
        }

        response = self.issue_request(url, params)
        return response['properties']['timeseries']
    
    def get_forecast_daily_mean(self, lat, lon):
        forecast = {}
        timeseries = self.get_forecast(lat, lon)
        for time in timeseries:
            date = time['time'][:10]
            if date not in forecast:
                forecast[date] = []
            forecast[date].append(time['data']['instant']['details']['air_temperature'])
        for date in forecast:
            forecast[date] = sum(forecast[date]) / len(forecast[date])
        return forecast

