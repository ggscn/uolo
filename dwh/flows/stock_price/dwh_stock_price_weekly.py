import resolve_imports
import time
import sys
import pandas as pd
from datetime import datetime
from dwh.models.stock_price import StockPriceWeekly
from dwh.lib.mboum import MBoumHTTP
from dwh.lib.seasonality import get_current_interval
from dwh.models.sqlalchemy_mixins import ModelMixin
from prefect import flow


ticker_select_statement = """ 
select * from company_tickers where exchange in ('Nasdaq','NYSE')
"""
max_date_select_statement = """
select cast(to_timestamp(max(day_utc_int)) as date) dt from stockpricesweekly where symbol = '{}'
"""
db = ModelMixin()


def get_ticker_max_stored_date(ticker):
    max_date = None
    select_statement = max_date_select_statement.format(ticker)
    max_date_result = db.query(
        select_statement, 
        to_df=True
    ).to_dict('records')
    if len(max_date_result) > 0:
        max_date = max_date_result[0]['dt'].strftime('%Y-%m-%d')
    return max_date

@flow(name='update-weekly-stock-prices')
def update_weekly_stock_prices():
    table = StockPriceWeekly()
    symbols = db.query(
        ticker_select_statement, to_df=True).to_dict('records')

    for i, symbol in enumerate(symbols):
        print(i, symbol['ticker'])
        max_date = get_ticker_max_stored_date(symbol['ticker'])
        df = pd.DataFrame(MBoumHTTP().get_weekly_history(
            symbol['ticker']).to_dict(symbol['cik']))
        df['day'] = pd.to_datetime(df['day'])
        if max_date is not None:
            df = df[df['day'] > max_date]
        df = df[df['day_utc_int'] != df['day_utc_int'].max()]
        table.append(df.to_dict('records'))
        time.sleep(0.15)

if __name__ == '__main__':
    update_weekly_stock_prices()



