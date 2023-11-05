import resolve_imports
import pandas as pd
from io import BytesIO
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker  
from dwh.models.sqlalchemy_mixins import ModelMixin
from dwh.lib.discord_bot import DiscordSyncBot
from datetime import date as dt, timedelta
from prefect import flow, task


model_query = """select * from lng_consumption_temperature_daily_models"""
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

def get_forecasted_consumption(model_df, weather_forecast, num_days=9):
    data = []
    for day in [(dt.today() + timedelta(x)) for x in range(1, num_days)]:
        historical_consumption_stats = model_df[
            model_df['day'] == day.strftime(f'{day.year-1}-%m-13')].to_dict('records')
        for country in historical_consumption_stats:
            expected_temperature = [x['average_temperature'] for x in weather_forecast 
                if x['day'].strftime('%Y-%m-%d') == day.strftime('%Y-%m-%d') 
                    and x['country'] == country['country']][0]
            hdd = country['average_temperature_day'] - expected_temperature
            expected_consumption = country['amount'] + (hdd * country['a_coefficient'])
            data.append({
                'day': day.strftime('%Y-%m-%d'),
                'country': country['country'],
                'consumption': expected_consumption,
                'historic_consumption': country['amount']
            })
    sum_df = pd.DataFrame(data).groupby(['day'], as_index=False).agg(
        {'consumption': 'sum', 'historic_consumption': 'sum'})
    send_timeseries_plot(sum_df)
    sum_df['perc_diff'] = ((sum_df['consumption'] - sum_df['historic_consumption']) / sum_df['consumption']) * 100
    send_perc_diff_plot(sum_df)
    return sum_df

def send_perc_diff_plot(df):
    plt.style.use("https://github.com/dhaitz/matplotlib-stylesheets/raw/master/pitayasmoothie-dark.mplstyle")
    plt.xticks(rotation = 45)
    plt.title('LNG consumption forecast (perc. diff)', pad=10)
    plt.bar(df['day'], df['perc_diff'],label='Temperature forecast adjusted LNG consumption against normal')
    plt.legend(loc=9, bbox_to_anchor=(0.5,-0.2))
    plt.gcf().subplots_adjust(bottom=0.15)
    with BytesIO() as image_binary:
        plt.savefig(image_binary, format='png', bbox_inches='tight')
        image_binary.seek(0)
        DiscordSyncBot().send(file_binary=image_binary)
    plt.clf()

def send_timeseries_plot(df):
    plt.style.use("https://github.com/dhaitz/matplotlib-stylesheets/raw/master/pitayasmoothie-dark.mplstyle")
    plt.xticks(rotation = 45)
    plt.title('LNG consumption forecast (absolute)', pad=10)
    plt.plot(df['day'], df['consumption'],label='Temperature forecast adjusted LNG consumption')
    plt.plot(df['day'], df['historic_consumption'],label='Historical avg. daily consumption (monthly)')
    plt.legend(title='Metrics:')
    plt.yticks(np.arange(min(0, min(df['consumption'])), max(0, max(df['consumption'])), 50))
    plt.gca().yaxis.set_major_formatter(mticker.FormatStrFormatter('%.0f MCM'))
    plt.gcf().subplots_adjust(bottom=0.15)
    with BytesIO() as image_binary:
        plt.savefig(image_binary, format='png')
        image_binary.seek(0)
        DiscordSyncBot().send(file_binary=image_binary)
    plt.close()

@flow(name='forecast-lng-consumption')
def forecast_lng_consumption():
    db = ModelMixin()
    model_df = get_model(db)
    weather_forecast = db.query(
        weather_forecast_query, to_df=True).to_dict('records')
    get_forecasted_consumption(
        model_df, weather_forecast)

if __name__ == '__main__':
    forecast_lng_consumption()


