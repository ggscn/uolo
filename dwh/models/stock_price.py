from sqlalchemy import Column, Integer, String, Float, Date, BigInteger
from sqlalchemy.orm import declarative_base
from .sqlalchemy_mixins import ModelMixin

Base = declarative_base()

class StockPrice(Base):
    __tablename__ = "stockprices"

    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    price = Column(Float)

class StockPriceWeekly(ModelMixin, Base):
    __tablename__ = 'stockpricesweekly'

    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    day_int = Column(Integer)
    day_utc_int = Column(Integer)
    day = Column(Date)
    volume = Column(BigInteger)
    open_price = Column(Float)
    close_price = Column(Float)
    adjusted_close_price = Column(Float)
    low_price = Column(Float)
    high_price = Column(Float)
    iso_week_number = Column(Integer)
    instrument_type = Column(String)
    cik = Column(String)
    

class StockPriceMonthly(ModelMixin, Base):
    __tablename__ = 'stockpricesmonthly'

    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    day_int = Column(Integer)
    day_utc_int = Column(Integer)
    day = Column(Date)
    volume = Column(BigInteger)
    open_price = Column(Float)
    close_price = Column(Float)
    adjusted_close_price = Column(Float)
    low_price = Column(Float)
    high_price = Column(Float)
    month = Column(Integer)
    instrument_type = Column(String)
    cik = Column(String)
