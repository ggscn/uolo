from prefect import flow, task
from models.company_fact import CompanyFact, CompanyFactAnalysis
from scipy.stats import linregress
from datetime import date
import sqlalchemy
import numpy as np
import pandas as pd


@task
def get_profit_loss_analysis(table, pandas_engine):
    query_str = """select "end", val, ticker
        from public.company_facts 
        where description = 'ProfitLoss' and fy > 2020 and val != 0 and frame is not null and length(frame) != 6
        order by ticker, "end" asc limit 50000
    """

    data_query_str_template = """SELECT val, ticker, description as fact_description, form as form_type, filed, frame
    from public.company_facts
    where description = 'ProfitLoss' and fy > 2020 and val != 0 and frame is not null and length(frame) != 6 and ticker = '{}'
    """

    df = pd.read_sql_query(query_str, con=pandas_engine)

    df['rolling_slope'] = (df.groupby('ticker')['val']
        .rolling(window=4)
        .apply(lambda v: linregress(np.arange(len(v)), v).slope )
        .reset_index(level=0, drop=True)
    )

    df = df.loc[df['end'] >= date(2022,12,31)]
    df = df.sort_values(['rolling_slope'], ascending=[False])
    df = df[:100]
    for i, ticker in enumerate(df.ticker.unique()):
        print(i, ticker)
        df = pd.read_sql_query(
            data_query_str_template.format(ticker), con=pandas_engine)
        df['analysis_label'] = 'Top 100 by Profit Loss Trend'
        table.append(df.to_dict('records'))
        

@flow(name="Update company facts")
def update_company_facts():
    url_object = sqlalchemy.engine.URL.create(
        "postgresql+psycopg2",
        username="pguser",
        password="pgpass",
        host="localhost",
        database="finance_dwh",
        port=5431
    )

    pandas_engine = sqlalchemy.create_engine(
        url_object)
    table = CompanyFactAnalysis(database='finance_flask_app_dev')
    table.truncate()
    get_profit_loss_analysis(table, pandas_engine)
    
if __name__ == '__main__':
    update_company_facts()