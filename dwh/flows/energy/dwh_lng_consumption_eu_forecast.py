import resolve_imports
import pandas as pd
from prefect import flow, task
from dwh.models.sqlalchemy_mixins import ModelMixin
from dwh.models.lng_consumption import LNGConsumptionTimeseriesForecast
import pandas as pd
from prophet import Prophet
pd.set_option('display.max_rows', None)

query_str = """ 
select 
 country_code, 
 amount, 
 time_period 
from 
 eu_lng_consumptions 
where 
 energy_balance = 'IC_OBS' and 
 unit = 'MIO_M3' and
 amount > 0
order by 
 time_period desc
"""
df = ModelMixin().query(query_str, to_df=True)
df = df[df['amount'].notna()]
df['month'] = pd.to_datetime(df['time_period'], format='%Y-%m-%d')
df = df[~(df['month'] < '2015-01-01')]
df['day'] = df['month'].apply(
    pd.date_range, freq='MS', periods=2).apply(
        lambda ds: pd.date_range(*ds, closed='left'))
df['amount'] /= df['day'].apply(len)
df = df.explode('day')
results = []
for country in df['country_code'].unique():
    country_consumption_df = df[df['country_code'] == country]
    country_consumption_df = pd.DataFrame({
        'ds': pd.to_datetime(country_consumption_df['day']),
        'y': country_consumption_df['amount']
    })
    cap = int(country_consumption_df['y'].max())
    if cap == 0:
        continue
    country_consumption_df['floor'] = 0
    country_consumption_df['cap'] = cap
    model = Prophet(growth='logistic')
    model.fit(country_consumption_df)
    future = model.make_future_dataframe(periods=180, freq='D')
    future['floor'] = 0
    future['cap'] = cap
    forecast = model.predict(future)
    forecast['country'] = country
    results.append(forecast)
df = pd.concat(results, ignore_index=True) 
df = df[['yhat', 'ds','country']]
df.rename(columns={'yhat':'consumption','ds':'day'}, inplace=True)
country_df = df.groupby('day').sum().reset_index()
country_df['country'] = 'EU'
results_df = pd.concat([country_df,df])
table = LNGConsumptionTimeseriesForecast()
table.truncate()
table.append(results_df.to_dict('records'))