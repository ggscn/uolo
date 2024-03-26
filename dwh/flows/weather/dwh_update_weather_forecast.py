import resolve_imports
import time
import pandas as pd
from dwh.models.country_weather_history import CountryWeatherHistory
from dwh.models.country_weather_forecast import CountryWeatherForecast
from prefect import flow, task
from dwh.lib.yr import YrQuery

def get_countries():
    country_query = "select country from country_weather_history group by country"
    historical_weather = CountryWeatherHistory().query(country_query)
    return [x['country'] for x in historical_weather]

@task
def list_cities(num_cities=25):
    cities_list = []
    cities = pd.read_csv('/home/pguser/code/raw_data/worldcities.csv')
    for country in get_countries():
        country_cities = cities[cities['iso2'] == country].sort_values(
            by='population', ascending=False)
        for city in country_cities.to_dict('records')[:num_cities]:
            city.update(country=country)
            cities_list.append(city)
    return cities_list

@flow(name='update-weather-forecasts')
def update_weather_forecasts():
    yr = YrQuery()
    data  = []
    for i, city in enumerate(list_cities()):
        time.sleep(1)
        print(i, city['city'])
        response = yr.get_forecast_daily_mean(city['lat'], city['lng'])
        for day, avg_temperature in response.items():
            data.append({
                'country': city['country'],
                'day': day,
                'average_temperature': avg_temperature,
                'city_name': city['city'],
                'lat': city['lat'],
                'lon': city['lng'],
                'city_population': city['population']
            })

    table = CountryWeatherForecast()
    table.drop()
    table.create()
    table.append(data)

if __name__ == '__main__':
    update_weather_forecasts()
    