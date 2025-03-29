import resolve_imports
from dwh.flows.energy.output_lng_consumption_weather_forecast import forecast_lng_consumption
from prefect.deployments import Deployment

deployment = Deployment.build_from_flow(
    flow=forecast_lng_consumption,
    name="lng-weather-forecast-deployment", 
    version=1, 
    work_queue_name="default",
)
deployment.apply()