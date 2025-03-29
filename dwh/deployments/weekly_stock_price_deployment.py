import resolve_imports
from dwh.flows.stock_price.dwh_stock_price_weekly import update_weekly_stock_prices
from prefect.deployments import Deployment

deployment = Deployment.build_from_flow(
    flow=update_weekly_stock_prices,
    name="weekly-stock-prices-deployment", 
    version=1, 
    work_queue_name="default",
)
deployment.apply()