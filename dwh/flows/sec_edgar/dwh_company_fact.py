import resolve_imports
from dwh.lib.edgar import EdgarRequest
from dwh.models.company_fact import CompanyFact
from dwh.models.company_ticker import CompanyTicker
from dwh.flows.sec_edgar.app_company_fact_analysis import update_app_company_fact_analysis
from prefect import flow, task
import time


@task(task_run_name="write-company-facts")
def write_company_facts(table):
    tickers = CompanyTicker.all()
    for i, ticker in enumerate(tickers):
        result = EdgarRequest().get_company_facts(
            ticker.cik).result(
                ticker=ticker.ticker,
                exchange=ticker.exchange,
                name=ticker.name
            )
        if result is not None:
            table.append(result)        
        time.sleep(0.11)


@flow(name="update-company-facts")
def update_company_facts():
    table = CompanyFact()
    table.truncate()
    write_company_facts(table)
    update_app_company_fact_analysis()
    
if __name__ == '__main__':
    update_company_facts()
    