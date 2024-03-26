import resolve_imports
from prefect import flow, task
from dwh.models.company_fact import CompanyFactAnalysis, CompanyFactAnalysisRank
from scipy.stats import linregress
import sqlalchemy
import numpy as np
import pandas as pd

rank_query_str_template = """
    WITH i1 AS (
    select 
      ticker, 
      count(*) as cnt 
    from 
      public.company_facts 
    where 
      description = '{}' and 
      fy > 2020 and val != 0 and  val is not null and
      frame is not null and 
      length(frame) != 6 
    group by 
      ticker
    )
    select 
      "end" as filing_day, 
      val, 
      ticker
    from 
      public.company_facts 
    where 
      description = '{}' and 
      fy > 2020 and val != 0 and 
       val is not null and
      frame is not null and 
      length(frame) != 6
      and ticker in (SELECT ticker from i1 where cnt > {})
    order by 
      ticker, "end" asc limit 50000
"""

series_query_str_template = """SELECT 
      val, 
      ticker, 
      description as fact_description, 
      form as form_type, 
      filed, 
      frame
    from 
      public.company_facts
    where 
      description = '{}' and 
      fy > 2020 and val != 0 and 
      frame is not null and 
      length(frame) != 6
"""

def get_pandas_db_engine():
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
    return pandas_engine

def init_tables(database, truncate):
    series_table = CompanyFactAnalysis()
    rank_table = CompanyFactAnalysisRank()
    if truncate:
        series_table.truncate()
        rank_table.truncate()
    return series_table, rank_table


@task
def write_fact_slope(fact_description, analysis_periods=4, database='finance_flask_app_dev', truncate_tables=False):
    pandas_engine = get_pandas_db_engine()
    series_table, rank_table = init_tables(database, truncate_tables)
    rank_query_str = rank_query_str_template.format(fact_description, fact_description, analysis_periods)
    df = pd.read_sql_query(rank_query_str, con=pandas_engine)

    df['analysis_value'] = (df.groupby('ticker')['val']
        .rolling(window=analysis_periods)
        .apply(lambda v: linregress(np.arange(len(v)), v).slope )
        .reset_index(level=0, drop=True)
    )

    #df = df.sort_values('filing_day', ascending=False).drop_duplicates(["ticker"])
    df = df.sort_values(['analysis_value'], ascending=[False])
    df['analysis_percentile_rank'] = (df['analysis_value'].rank(pct=True) * 100).round().fillna(0.0).astype(int)
    df['analysis_rank'] = df.reset_index().index + 1
    df['analysis_label'] = 'Slope'
    df['analysis_periods'] = analysis_periods
    df['fact_description'] = fact_description
    rank_table.append(df.to_dict('records'))
    
    series_query_str = series_query_str_template.format(
        fact_description)
    df = pd.read_sql_query(series_query_str, con=pandas_engine)
    df['analysis_label'] = 'Slope'
    series_table.append(df.to_dict('records'))
        

@flow(name="update-app-company-fact-analysis")
def update_app_company_fact_analysis():
    for i, fact_description in enumerate(['InterestPaidNet','ProfitLoss']):
        if i == 0:
            write_fact_slope(fact_description, truncate_tables=True)
        else:
            write_fact_slope(fact_description, truncate_tables=False)
    
if __name__ == '__main__':
    update_app_company_fact_analysis()