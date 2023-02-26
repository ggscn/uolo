from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from .sqlalchemy_mixins import ModelMixin

Base = declarative_base()

class CompanyTicker(Base, ModelMixin):
    __tablename__ = 'company_tickers'

    id = Column(Integer, primary_key=True)
    cik = Column(String)
    name = Column(String)
    ticker = Column(String)
    exchange = Column(String)
