import sys
from pathlib import Path # if you haven't already done so
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[2]
sys.path.append(str(root))
import discord
import pandas as pd
from contextlib import suppress
from uuid import uuid4
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime
from dwh.models.sqlalchemy_mixins import ModelMixin
from table2ascii import table2ascii as t2a, PresetStyle


symbols_query_str = """select symbol, count(*) cnt, avg(volume) volume from stockpricesmonthly group by symbol order by symbol"""

ticker_seasonality_query_template = """select 
 {},
 {},
 day
from
 stockprices{} 
where 
 symbol = '{}'
order by 
 day
"""

keyword_symbols_query_template = """ 
select 
  a.symbol
from
  company_tickers
where 
  name ilike '%%{}%%'
"""

interval_columns = {
    'weekly': 'iso_week_number',
    'monthly': 'month'
}

def get_current_interval(interval):
    if interval == 'weekly':
        current_interval = datetime.now().isocalendar()[1]
    else:
        current_interval = datetime.now().month
    return current_interval


def get_seasonality(symbol, interval, price_column='close_price', interval_value=None):
    interval_column  = interval_columns[interval]
    query_str = ticker_seasonality_query_template.format(
        interval_column, price_column,interval,symbol.upper())
    db = ModelMixin()
    if interval_value is None:
        interval_value = get_current_interval(interval)
    df = db.query(query_str, to_df=True)
    df = df.sort_values(by='day')
    df['interval_percent_change'] = df[price_column].pct_change() * 100
    df = df.dropna()
    df = df[[interval_column, 'interval_percent_change','day']]
    
    df = df.groupby(interval_column).agg(
        interval_mean=('interval_percent_change', 'mean'),
        confidence_interval_low=('interval_percent_change', lambda x: np.percentile(x,5)),
        confidence_interval_high=('interval_percent_change', lambda x: np.percentile(x, 95)),
        interval_std=('interval_percent_change', 'std')
    ).reset_index()
    seasonality = df[df[interval_column] == interval_value].to_dict(
        'records')[0]
    return df, seasonality


def get_keyword_seasonality(search_term, interval, price_column='close_price'):
    interval_column  = interval_columns[interval]
    symbol_seasonality = []
    seasonality_dfs = []
    db = ModelMixin()
    symbols = db.query(
        keyword_symbols_query_template.format(search_term), to_df=True)
    for symbol in symbols.symbol.unique():
        ticker_seasonality, seasonality = get_seasonality(symbol, interval, price_column)
        seasonality_dfs.append(ticker_seasonality)
        symbol_seasonality.append({'symbol': symbol,'seasonality':seasonality['interval_mean']})
    seasonality_df = pd.concat(seasonality_dfs)
    seasonality = pd.DataFrame(symbol_seasonality)['seasonality'].mean()

    df = seasonality_df.groupby([interval_column], as_index=False).agg(
        {'weekly_percent_change': 'mean'})
    return df, seasonality


def get_seasonality_chart(interval, symbol=None, keyword=None, price_column='close_price'):
    interval_column  = interval_columns[interval]
    if symbol is not None:
        df, seasonality = get_seasonality(symbol, interval, price_column)
    elif keyword is not None:
        df, seasonality = get_keyword_seasonality(symbol, interval, price_column)
    plt.style.use('https://github.com/dhaitz/matplotlib-stylesheets/raw/master/pitayasmoothie-dark.mplstyle')
    
    plt.fill_between(df[interval_column],
        df['confidence_interval_low'],
        df['confidence_interval_high'],
        color='skyblue', 
        alpha=0.15, 
        label='CI (95%)'
    )
    
    plt.errorbar(df[interval_column], df['interval_mean'],
        yerr=df['interval_std'],
        fmt='o', 
        ecolor='lightcoral', 
        elinewidth=1, 
        capsize=5,
        c='lightcoral',
        label=f'Average {symbol} m/m returns and Std dev'
    )

    plt.title(f' 5y {symbol.upper()} {interval} Seasonality', pad=10)
    plt.xticks(rotation = 45)
    plt.legend(loc=9, bbox_to_anchor=(0.5,-0.2))
    plt.grid(alpha=0.1)
    plt.axhline(y=0,linestyle='--')
    with BytesIO() as image_binary:
        plt.savefig(image_binary, format='png', bbox_inches='tight')
        image_binary.seek(0)
        file = discord.File(fp=image_binary, filename=str(uuid4())+'.png')
        return f'{seasonality["interval_mean"]:.2f}% for {interval.replace("ly","")} {get_current_interval(interval)}', file


def ranked_seasonality(interval, max_seasonality=50, min_volume=0, interval_value=None):
    seasonalities = []
    df = ModelMixin().query(symbols_query_str, to_df=True)
    df = df[df['cnt'] > 20]
    df = df[df['volume'] > min_volume]
    for i, symbol in enumerate(df.symbol.unique()):
        with suppress(Exception):
            df, seasonality = get_seasonality(symbol, interval, interval_value=interval_value)
            #seasonality['rank'] = seasonality['interval_mean'] - 1 / (seasonality['confidence_interval_high'] - seasonality['confidence_interval_low'])
            interval_width = seasonality['confidence_interval_high'] - seasonality['confidence_interval_low']
            seasonality['rank'] = seasonality['interval_mean'] - 1 / (interval_width ** 3)
            seasonalities.append({'symbol': symbol, 'seasonality': round(seasonality['interval_mean'],2), 'rank':round(seasonality['rank'],2)})
    df = pd.DataFrame(seasonalities)
    df = df[df['seasonality'] < max_seasonality]
    df = df.sort_values(by='rank', ascending=False)

    output = t2a(
        header=[x for x in df.columns],
        body=[x for x in df.values.tolist()][:50],
        first_col_heading=True
    )
    return output