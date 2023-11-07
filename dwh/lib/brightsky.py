import requests
import pandas as pd

class BrightSkyQuery:
    def __init__(self) -> None:
        self.base_url = 'https://api.brightsky.dev/'

    def issue_request(self, url, params):
        headers = {'Accept': 'application/json'}
        response = requests.get(
            url, params=params, headers=headers).json()
        
        return response

    def get_weather(self, lat, lon, start_date, end_date):
        url = self.base_url + '/weather'
        params = {
            'lat': lat,
            'lon': lon,
            'date': start_date,
            'last_date': end_date
        }

        response = self.issue_request(url, params)
        if 'title' in response:
            print(response)
        return response['weather']
    
    def get_daily_historical_temperature(self, lat, lon, start_date, end_date):
        data = []
        date_temperatures = {}
        timeseries = self.get_weather(
            lat, lon, start_date, end_date)
        for time in timeseries:
            date = time['timestamp'][:10]
            if date not in date_temperatures:
                date_temperatures[date] = []
            if time['temperature'] is not None:
                date_temperatures[date].append(time['temperature'])
        for date in date_temperatures:
            if len(date_temperatures[date]) == 0:
                continue
            data.append({
                'date': date,
                'average_temperature': sum(date_temperatures[date]) / len(date_temperatures[date]),
                'max_temp': max(date_temperatures[date]),
                'min_temp': min(date_temperatures[date]),
                'lat': lat,
                'lon': lon
            })
        return data