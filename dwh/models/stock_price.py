from sqlalchemy import Column, Integer, String, Float, Date
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class StockPrice(Base):
    __tablename__ = "stockprices"

    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    price = Column(Float)

