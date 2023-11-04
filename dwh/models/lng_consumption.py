from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.orm import declarative_base
from .sqlalchemy_mixins import ModelMixin

Base = declarative_base()
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
