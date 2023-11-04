from sqlalchemy import Column, Integer, String, Float, Date
from sqlalchemy.orm import declarative_base
from .sqlalchemy_mixins import ModelMixin

Base = declarative_base()

class CountryWeatherHistory(ModelMixin, Base):
    __tablename__ = "country_weather_history"

    id = Column(Integer, primary_key=True)
    country = Column(String)
    day = Column(Date)
    average_temperature = Column(Float)
    average_temperature_day = Column(Float)
    avg_max_temp = Column(Float)
    avg_min_temp = Column(Float)
    hdd = Column(Float)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)