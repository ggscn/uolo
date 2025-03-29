from sqlalchemy import Column, Integer, String, Float, Date, BigInteger
from sqlalchemy.orm import declarative_base
from .sqlalchemy_mixins import ModelMixin

Base = declarative_base()

class ReportingOwner(ModelMixin, Base):
    __tablename__ = 'reporting_owners'

    id = Column(Integer, primary_key=True)
    accession_number = Column(String)
    rptownercik = Column(String)
    rptownername = Column(String)
    rptowner_relationship = Column(String)
    rptowner_title = Column(String)
    rptowner_txt = Column(String)
    rptowner_street1 = Column(String)
    rptowner_street2 = Column(String)
    rptowner_city = Column(String)
    rptowner_state = Column(String)
    rptowner_zipcode = Column(String)
    rptowner_state_desc = Column(String)
    file_number = Column(String)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



