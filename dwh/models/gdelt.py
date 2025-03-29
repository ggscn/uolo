from sqlalchemy import Column, Integer, String, Float, Date, BigInteger
from sqlalchemy.orm import declarative_base
from .sqlalchemy_mixins import ModelMixin

Base = declarative_base()

class GdeltGKG(ModelMixin, Base):
    __tablename__ = "gdelt_gkg"

    gkgrecordid = Column(String) 
    date = Column(BigInteger)
    sourcecollectionidentifier = Column(Integer)
    sourcecommonname = Column(String)
    documentidentifier = Column(String)
    v2counts = Column(String)
    v2themes = Column(String)
    v2locations  = Column(String)
    v2persons = Column(String)
    v2organizations = Column(String)
    v2tone = Column(String)
    dates = Column(String)
    gcam = Column(String)
    sharingimage = Column(String)
    quotations = Column(String)
    allnames = Column(String)
    amounts = Column(String)
    translationinfo = Column(String)
    extras = Column(String)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)