import resolve_imports
import time
import sys
import pandas as pd
from datetime import datetime
from dwh.models.stock_price import StockPriceMonthly
from dwh.lib.mboum import MBoumHTTP
from dwh.models.sqlalchemy_mixins import ModelMixin
from prefect import flow


ticker_select_statement = """ 
select * from company_tickers where exchange in ('Nasdaq','NYSE') and ticker not in (select symbol from stockpricesmonthly WHERE symbol IS NOT NULL group by symbol)
"""
max_date_select_statement = """
select max(day) dt from stockpricesmonthly where symbol = '{}'
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

@flow(name='update-monthly-stock-prices')
def update_monthly_stock_prices():
    table = StockPriceMonthly()
    symbols = db.query(
        ticker_select_statement, to_df=True).to_dict('records')

    for i, symbol in enumerate(symbols):
        print(i, symbol['ticker'])
        #max_date = get_ticker_max_stored_date(symbol['ticker'])
        max_date = None
        df = pd.DataFrame(MBoumHTTP().get_monthly_history(
            symbol['ticker']).to_dict(symbol['cik']))
        """df['day'] = pd.to_datetime(df['day'])
        if max_date is not None:
            df = df[df['day'] > max_date]"""
        table.append(df.to_dict('records'))
        time.sleep(0.15)

if __name__ == '__main__':
    if datetime.today().weekday() not in [5,6]:
        update_monthly_stock_prices()



