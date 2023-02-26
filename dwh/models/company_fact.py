from sqlalchemy import Column, Integer, String, Float, Date, BigInteger
from sqlalchemy.orm import declarative_base
from .sqlalchemy_mixins import ModelMixin

Base = declarative_base()

class CompanyFact(ModelMixin, Base):
    __tablename__ = 'company_facts'

    id = Column(Integer, primary_key=True)
    cik = Column(String)
    name = Column(String)
    ticker = Column(String)
    exchange = Column(String)
    end = Column(Date)
    val = Column(BigInteger)
    form = Column(String)
    fy = Column(Integer)
    fp = Column(String)
    description = Column(String)
    currency = Column(String)
    accn = Column(String)
    rule_set = Column(String)
    frame = Column(String)
    filed = Column(String)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)