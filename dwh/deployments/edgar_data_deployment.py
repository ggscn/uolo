import resolve_imports
from dwh.flows.sec_edgar.dwh_company_ticker import update_company_tickers
from prefect.deployments import Deployment

deployment = Deployment.build_from_flow(
    flow=update_company_tickers,
    name="edgar-data-deployment", 
    version=1, 
    work_queue_name="default",
)
deployment.apply()