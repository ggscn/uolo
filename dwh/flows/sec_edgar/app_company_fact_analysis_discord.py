import resolve_imports
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker  
from io import BytesIO
from prefect import flow, task
from dwh.lib.discord_sync import DiscordSyncBot
from dwh.models.sqlalchemy_mixins import ModelMixin

import sqlalchemy
pd.set_option('display.max_rows', None)

db = ModelMixin()


query_str = """ 
select 
 ticker, analysis_value, filing_day,analysis_rank
 from
 company_fact_analysis_ranks where fact_description = 'ProfitLoss' and analysis_label='Slope' and analysis_periods > 2 and analysis_value is not null
order by 
 analysis_rank, ticker, filing_day
"""

df = db.query(query_str, to_df=True)
df = df.sort_values(by=['analysis_rank','ticker'])
for ticker in df.ticker.unique()[:15]:
    ticker_df =  db.query(f"select frame, val from company_fact_analyses where ticker = '{ticker}' and fact_description = 'ProfitLoss' and analysis_label = 'Slope'", to_df=True)
    ticker_df['val'] = ticker_df['val'] / 1000000
    ticker_df = ticker_df.sort_values(by='frame')
    print(ticker_df.to_dict('records'))
    plt.style.use("https://github.com/dhaitz/matplotlib-stylesheets/raw/master/pitayasmoothie-dark.mplstyle")
    plt.xticks(rotation = 45)
    plt.title(f'Profitloss by Quarter - {ticker}', pad=10)
    plt.plot(ticker_df['frame'], ticker_df['val'],label='Profitloss')
    plt.legend(title='Metrics:')
    plt.gca().yaxis.set_major_formatter(mticker.FormatStrFormatter('%.0f $ MM'))
    plt.gcf().subplots_adjust(bottom=0.15, left=0.2)
    with BytesIO() as image_binary:
        plt.savefig(image_binary, format='png')
        image_binary.seek(0)
        DiscordSyncBot('stocks').send(file_binary=image_binary)
    plt.close()