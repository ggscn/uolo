from sqlalchemy import Column, Integer, String, DateTime, Float, Date
from sqlalchemy.orm import declarative_base
from .sqlalchemy_mixins import ModelMixin

Base = declarative_base()

class LNGConsumptionTemperatureDailyModel(ModelMixin, Base):
    __tablename__ = 'lng_consumption_temperature_daily_models'

    id = Column(Integer, primary_key=True)
    country = Column(String)
    day = Column(Date)
    average_temperature = Column(Float)
    average_temperature_day = Column(Float)
    avg_max_temp = Column(Float)
    avg_min_temp = Column(Float)
    hdd = Column(Float)
    amount = Column(Float)
    time_period = Column(String)
    month = Column(DateTime)
    a_coefficient = Column(Float)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LNGConsumptionForecast(ModelMixin, Base):
    __tablename__ = 'lng_consumption_forecasts'

    id = Column(Integer, primary_key=True)
    run_time = Column(DateTime)
    day = Column(Date)
    consumption = Column(Float)
    historic_consumption = Column(Float)
    perc_diff = Column(Float)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
class LNGConsumptionTimeseriesForecast(ModelMixin, Base):
    __tablename__ = 'lng_consumption_timeseries_forecasts'

    id = Column(Integer, primary_key=True)
    day = Column(Date)
    consumption = Column(Float)
    country = Column(String)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class LNGConsumptionEU(ModelMixin, Base):
    __tablename__ = 'eu_lng_consumptions'

    id = Column(Integer, primary_key=True)
    frequency = Column(String)
    energy_balance = Column(String)
    energy_balance_type = Column(String)
    product_classification = Column(String)
    country_code = Column(String)
    time_period = Column(String)
    unit = Column(String)
    amount = Column(Float)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LNGConsumptionUS(ModelMixin, Base):
    __tablename__ = 'us_lng_consumptions'

    id = Column(Integer, primary_key=True)
    frequency = Column(String)
    energy_balance = Column(String)
    energy_balance_type = Column(String)
    product_classification = Column(String)
    country_code = Column(String)
    time_period = Column(String)
    unit = Column(String)
    amount = Column(Float)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
