import resolve_imports
import pandas as pd
from prefect import flow, task
from sklearn.linear_model import LinearRegression
from dwh.models.sqlalchemy_mixins import ModelMixin
from dwh.models.lng_consumption import LNGConsumptionTemperatureDailyModel

temperature_df_query = """
select 
 country,
 day,
 average_temperature,
 avg_max_temp,
 avg_min_temp,
 average_temperature_day,
 hdd
from 
 country_weather_history 
"""

gas_consumption_df_query = """
select 
 country_code country, 
 amount, 
 time_period 
from 
 eu_lng_consumptions 
where 
 energy_balance = 'IC_OBS' and 
 unit = 'MIO_M3' 
order by 
 time_period desc
"""

def get_weather_history():
    temperature_df = ModelMixin().query(
        temperature_df_query, to_df=True)
    temperature_df['day'] = pd.to_datetime(
        temperature_df['day'], format='%Y-%m-%d')
    return temperature_df


def get_gas_consumption_history():
    gas_consumption_df = ModelMixin().query(
        gas_consumption_df_query, to_df=True)

    gas_consumption_df = gas_consumption_df[
        gas_consumption_df['amount'].notna()]
    gas_consumption_df['month'] = pd.to_datetime(
        gas_consumption_df['time_period'], format='%Y-%m-%d')
    gas_consumption_df = gas_consumption_df[
        ~(gas_consumption_df['month'] < '2015-01-01')]
    gas_consumption_df = gas_consumption_df[
        ~(gas_consumption_df['month'] > '2022-12-31')]
    gas_consumption_df['day'] = gas_consumption_df['month'].apply(
        pd.date_range, freq='MS', periods=2).apply(
            lambda ds: pd.date_range(*ds, closed='left'))
    gas_consumption_df['amount'] /= gas_consumption_df['day'].apply(len)
    gas_consumption_df = gas_consumption_df.explode('day')
    gas_consumption_df['day'] = pd.to_datetime(
        gas_consumption_df['day'])
    return gas_consumption_df

@task
def model_lng_consumption():
    temperature_df = get_weather_history()
    gas_consumption_df = get_gas_consumption_history()

    model_df = temperature_df.merge(
        gas_consumption_df, on=['country', 'day'], how='inner')

    for country, group in model_df.groupby('country'):
        regression_model = LinearRegression()
        X = group[['hdd']].values
        y = group['amount'].values
        regression_model.fit(X, y)
        a_coefficient = regression_model.coef_[0]
        model_df.loc[model_df['country'] == country, 
            'a_coefficient'] = a_coefficient
    return model_df.to_dict('records')

@flow(name='update-lng-daily-temperature-consumption-model')
def save_daily_lng_consumption_model():
    model_data = model_lng_consumption()
    table = LNGConsumptionTemperatureDailyModel()
    table.truncate()
    table.append(model_data)

if __name__ == '__main__':
    save_daily_lng_consumption_model()