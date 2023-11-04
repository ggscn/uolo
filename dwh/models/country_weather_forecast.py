from sqlalchemy import Column, Integer, String, Float, Date
from sqlalchemy.orm import declarative_base
from .sqlalchemy_mixins import ModelMixin

Base = declarative_base()


class CountryWeatherForecast(ModelMixin, Base):
    __tablename__ = "country_weather_forecasts"

    id = Column(Integer, primary_key=True)
    country = Column(String)
    city_name = Column(String)
    city_population = Column(Float)
    day = Column(Date)
    average_temperature = Column(Float)
    lat = Column(Float)
    lon = Column(Float)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)