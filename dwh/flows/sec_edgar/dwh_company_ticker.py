import resolve_imports
from dwh.lib.edgar import EdgarRequest
from dwh.models.company_ticker import CompanyTicker
from dwh.flows.sec_edgar.dwh_company_fact import update_company_facts
from prefect import flow, task

@task
def get_company_tickers():
    results = EdgarRequest().get_company_tickers().results()
    return results

@flow(name="update-company-tickers")
def update_company_tickers():
    company_tickers = get_company_tickers()
    table = CompanyTicker()
    table.truncate()
    table.append(company_tickers)
    update_company_facts()
    
if __name__ == '__main__':
    update_company_tickers()