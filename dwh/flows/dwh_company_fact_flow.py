import resolve_imports
from dwh.lib.edgar import EdgarRequest
from dwh.models.company_fact import CompanyFact
from dwh.models.company_ticker import CompanyTicker
from dwh.flows.app_company_fact_analysis_flow import update_app_company_fact_analysis
from prefect import flow, task
import time


@task(task_run_name="write-company-{ticker_name}")
def write_company_facts(table, ticker, ticker_name):
    result = EdgarRequest().get_company_facts(
        ticker.cik).result(
            ticker=ticker.ticker,
            exchange=ticker.exchange,
            name=ticker.name
        )
    if result is not None:
        table.append(result)
        

@flow(name="update-company-facts")
def update_company_facts():
    
    table = CompanyFact()
    table.truncate()
    tickers = CompanyTicker.all()
    for i, ticker in enumerate(tickers):
        write_company_facts(table, ticker, ticker.name)
        time.sleep(0.11)
    update_app_company_fact_analysis()
    
if __name__ == '__main__':
    update_company_facts()
    