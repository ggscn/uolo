from lib.edgar import EdgarRequest
from lib.table import Table
from prefect import flow, task
from models.company_ticker import CompanyTicker


@task
def get_company_tickers():
    results = EdgarRequest().get_company_tickers().results()
    return results

@flow(name="Get company tickers")
def update_company_tickers():
    company_tickers = get_company_tickers()
    table = Table(CompanyTicker)
    table.drop()
    table.create()
    table.append(company_tickers)
    
if __name__ == '__main__':
    update_company_tickers()