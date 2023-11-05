#https://opendata.stackexchange.com/questions/10154/sources-of-weather-data/10155
#us weather https://www.weather.gov/documentation/services-web-api#/default/products_type_location
import resolve_imports
import pandas as pd
import numpy as np
from dwh.models.country_weather_history import CountryWeatherHistory
from prefect import flow, task

@task
def get_eu_weather():
    Tref = 18
    temperature_df = pd.read_csv('/home/pguser/code/raw_data/europeweather.csv')
    temperature_df['date'] = pd.to_datetime(temperature_df['date'])
    temperature_df['day'] = pd.to_datetime(temperature_df['date'].dt.strftime('%Y-%m-%d'))
    temperature_df = temperature_df[~(temperature_df['day'] < '2015-01-01')]
    temperature_df = temperature_df[~(temperature_df['day'] > '2022-12-31')]
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
    weather_history = []
    eu_weather_history = get_eu_weather()
    weather_history.extend(eu_weather_history)
    table.truncate()
    table.append(weather_history)

if __name__ == '__main__':
    backfill_historical_weather()