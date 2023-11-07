#https://opendata.stackexchange.com/questions/10154/sources-of-weather-data/10155
#us weather https://www.weather.gov/documentation/services-web-api#/default/products_type_location
import resolve_imports
import pandas as pd
import numpy as np
from datetime import date
from dwh.models.country_weather_history import CountryWeatherHistory
from dwh.lib.brightsky import BrightSkyQuery
from prefect import flow, task

@task
def get_eu_weather():
    eu_weather = pd.read_csv('/home/pguser/code/raw_data/europeweather.csv')
    eu_weather['date'] = pd.to_datetime(eu_weather['date'])
    eu_weather['day'] = pd.to_datetime(eu_weather['date'].dt.strftime('%Y-%m-%d'))
    eu_weather = eu_weather[~(eu_weather['day'] < '2015-01-01')]
    eu_weather = eu_weather[~(eu_weather['day'] > '2022-12-31')]
    return eu_weather


def get_de_weather(num_cities=25):
    weather_data = []
    cities = pd.read_csv('/home/pguser/code/raw_data/worldcities.csv')
    for year in range(2015, date.today().year):
        for city in cities[cities['iso2'] == 'DE'].sort_values(
                by='population', ascending=False).to_dict('records')[:num_cities]:
            print(city['city'], year)
            weather_data.extend(BrightSkyQuery().get_daily_historical_temperature(
                city['lat'],city['lng'], f'{year}-01-01',f'{year}-12-31'))
    de_weather = pd.DataFrame(weather_data)
    de_weather = de_weather.groupby(['date']).agg({
        'average_temperature': 'mean', 'max_temp': 'mean', 'min_temp': 'mean'
    }).reset_index()
    de_weather.rename(columns={'max_temp': 'avg_max_temp', 'min_temp': 'avg_min_temp'}, inplace=True)
    de_weather['country'] = 'DE'
    de_weather['date'] = pd.to_datetime(de_weather['date'])
    de_weather['day'] = pd.to_datetime(de_weather['date'].dt.strftime('%Y-%m-%d'))
    return de_weather
        

def process_weather():
    Tref = 18
    temperature_df = pd.concat([
        get_de_weather(), get_eu_weather()])
    temperature_df['average_temperature'] = (5/9) * (temperature_df['average_temperature'] - 32)
    temperature_df['hdd'] = np.maximum(0, Tref - temperature_df['average_temperature'])
    temperature_df['day_month'] = temperature_df['day'].dt.strftime('%m-%d')
    average_temperatures = temperature_df.groupby(['day_month','country'])['average_temperature'].mean().reset_index()
    temperature_df = temperature_df.merge(average_temperatures, on=['day_month', 'country'], how='left')
    temperature_df.rename(columns={'average_temperature_x': 'temperature_x', 'average_temperature_y': 'average_temperature_day'}, inplace=True)
    temperature_df.drop(columns=['day_month', 'date','temperature_x'], inplace=True)
    return temperature_df.to_dict('records')


@flow(name='backfill-historical-weather')
def backfill_historical_weather():
    table = CountryWeatherHistory()
    eu_weather_history = process_weather()
    table.truncate()
    table.append(eu_weather_history)

if __name__ == '__main__':
    backfill_historical_weather()