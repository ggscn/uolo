from lib.edgar import EdgarRequest
from prefect import flow, task
from models.company_fact import CompanyFact
from models.company_ticker import CompanyTicker
import time


@task
def get_tickers(table):
    tickers = CompanyTicker.all()
    for i, ticker in enumerate(tickers):
        print(ticker.ticker, ticker.name, i) 
        result = EdgarRequest().get_company_facts(
            ticker.cik).result(
                ticker=ticker.ticker,
                exchange=ticker.exchange,
                name=ticker.name
            )
        if result is not None:
            table.append(result)
        time.sleep(0.11)
        

@flow(name="Update company facts")
def update_company_facts():
    
    table = CompanyFact()
    table.truncate()
    get_tickers(table)
    
if __name__ == '__main__':
    update_company_facts()