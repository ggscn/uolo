import resolve_imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker  
from io import BytesIO
from prefect import flow, task
from datetime import date as dt, timedelta
from dwh.lib.discord_sync import DiscordSyncBot
from dwh.models.sqlalchemy_mixins import ModelMixin
from dwh.models.lng_consumption import LNGConsumptionForecast
from dwh.flows.weather.dwh_update_weather_forecast import update_weather_forecasts


model_query = """select * from lng_consumption_temperature_daily_models"""
lng_timeseries_forecast_query = """select * from lng_consumption_timeseries_forecasts where country!='EU'"""
weather_forecast_query = """select 
country,
day,
sum(average_temperature * city_population) / sum(city_population) average_temperature
from 
country_weather_forecasts 
 group by country, day
"""


def get_model(db):
    model_df = db.query(model_query, to_df=True)
    model_df['day'] = pd.to_datetime(model_df['day'])
    return model_df


def get_forecasted_consumption(model_df, weather_forecast, timeseries_forecasted_consumption, num_days=10):
    data = []
    for day in [(dt.today() + timedelta(x)) for x in range(1, num_days)]:
        historical_consumption_stats = model_df[
            model_df['day'] == day.strftime(f'{day.year-1}-%m-{day.day}')].to_dict('records')
        for country in historical_consumption_stats:
            if country['country'] in ['CY']:
                continue
            expected_temperature = [x['average_temperature'] for x in weather_forecast 
                if x['day'].strftime('%Y-%m-%d') == day.strftime('%Y-%m-%d') 
                    and x['country'] == country['country']][0]
            forecasted_consumption = [x['consumption'] for x in timeseries_forecasted_consumption 
                if x['day'].strftime('%Y-%m-%d') == day.strftime('%Y-%m-%d') 
                    and x['country'] == country['country']][0]
            hdd = country['average_temperature_day'] - expected_temperature
            expected_consumption = forecasted_consumption + (hdd * country['a_coefficient'])
            data.append({
                'day': day.strftime('%Y-%m-%d'),
                'country': country['country'],
                'consumption': expected_consumption,
                'historic_consumption': country['amount'],
                'forecasted_consumption': forecasted_consumption
            })
    sum_df = pd.DataFrame(data).groupby(['day'], as_index=False).agg(
        {'consumption': 'sum', 'historic_consumption': 'sum','forecasted_consumption':'sum'})
    perc_diff = ((sum_df['consumption'].sum() - sum_df['forecasted_consumption'].sum()) / sum_df['consumption'].sum()) * 100
    send_timeseries_plot(sum_df, perc_diff)
    return sum_df.to_dict('records')


def send_perc_diff_plot(df):
    plt.style.use("https://github.com/dhaitz/matplotlib-stylesheets/raw/master/pitayasmoothie-dark.mplstyle")
    plt.xticks(rotation = 45)
    plt.title('EU LNG consumption forecast (perc. diff)', pad=10)
    plt.bar(df['day'], df['perc_diff'],label='Temperature forecast adjusted LNG consumption against normal')
    plt.legend(loc=9, bbox_to_anchor=(0.5,-0.2))
    plt.gcf().subplots_adjust(bottom=0.15)
    with BytesIO() as image_binary:
        plt.savefig(image_binary, format='png', bbox_inches='tight')
        image_binary.seek(0)
        DiscordSyncBot().send(file_binary=image_binary)
    plt.clf()


def send_timeseries_plot(df, perc_diff):
    plt.style.use("https://github.com/dhaitz/matplotlib-stylesheets/raw/master/pitayasmoothie-dark.mplstyle")
    plt.xticks(rotation = 45)
    plt.title(f'EU gas consumption forecast - {perc_diff:.2f}% deviation next 10D', pad=10)
    plt.plot(df['day'], df['consumption'],label='Temperature-adjusted gas consumption forecast')
    plt.plot(df['day'], df['forecasted_consumption'],label='Gas consumption forecast')
    plt.plot(df['day'], df['historic_consumption'],label='LY avg. daily consumption')
    plt.legend(title='Metrics:')
    plt.yticks(np.arange(min(0, min(df['consumption'])), max(0, max(df['consumption'])), 100))
    plt.gca().yaxis.set_major_formatter(mticker.FormatStrFormatter('%.0f MCM'))
    plt.gcf().subplots_adjust(bottom=0.15)
    with BytesIO() as image_binary:
        plt.savefig(image_binary, format='png')
        image_binary.seek(0)
        DiscordSyncBot().send(file_binary=image_binary)
    plt.close()


@flow(name='forecast-lng-consumption')
def forecast_lng_consumption():
    update_weather_forecasts()
    db = ModelMixin()
    model_df = get_model(db)
    weather_forecast = db.query(
        weather_forecast_query, to_df=True).to_dict('records')
    timeseries_forecasted_consumption = db.query(
        lng_timeseries_forecast_query, to_df=True).to_dict('records')
    forecasted_consumption = get_forecasted_consumption(
        model_df, weather_forecast, timeseries_forecasted_consumption)
    table = LNGConsumptionForecast()
    #table.append(forecasted_consumption)
    

if __name__ == '__main__':
    forecast_lng_consumption()


