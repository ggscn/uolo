import resolve_imports
from dwh.flows.dwh_weather_forecast_flow import get_weather_forecasts
from prefect.deployments import Deployment

deployment = Deployment.build_from_flow(
    flow=get_weather_forecasts,
    name="weather-forecast-deployment", 
    version=1, 
    work_queue_name="default",
)
deployment.apply()