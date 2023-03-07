import enum
from flask import current_app
from collections import OrderedDict
from datetime import datetime, timedelta

from sqlalchemy import DateTime, Date, Column, Integer, String, Boolean, Enum, Float, ForeignKey, and_, Numeric, desc, BigInteger
from sqlalchemy.orm import relationship, backref

from lib.sqlalchemy_utils import ModelUtils, EnumUtils
from lib.company import Tiingo
from flask_app.extensions import db

class CompanyFactAnalysisRank(db.Model, ModelUtils):
    __tablename__ = 'company_fact_analysis_ranks'

    id = Column(Integer, primary_key=True)

    ticker = Column(String())
    analysis_label = Column(String())
    analysis_value = Column(Float())
    analysis_rank = Column(Integer())
    analysis_percentile_rank = Column(Integer())
    analysis_periods = Column(Integer())
    fact_description = Column(String())
    filing_day = Column(Date)

    def __init__(self, **kwargs):
        super(CompanyFactAnalysisRank, self).__init__(**kwargs)
    
    @classmethod
    def get_company_fact(cls, analysis_label, indicator):
        results = CompanyFactAnalysisRank.query.with_entities(
            CompanyFactAnalysisRank.ticker,
            CompanyFactAnalysisRank.analysis_rank
        ).filter(and_(
            CompanyFactAnalysisRank.analysis_label == analysis_label,
            CompanyFactAnalysisRank.fact_description == indicator
        )).distinct().order_by(
            CompanyFactAnalysisRank.analysis_rank
        ).limit(500)
        return results

class CompanyFactAnalysis(db.Model, ModelUtils):
    __tablename__ = 'company_fact_analyses'

    id = Column(Integer, primary_key=True)

    val = Column(BigInteger())
    ticker = Column(String())
    fact_description = Column(String())
    form_type = Column(String())
    filed = Column(String())
    frame = Column(String())
    analysis_label = Column(String())

    def __init__(self, **kwargs):
        super(CompanyFactAnalysis, self).__init__(**kwargs)

    @classmethod
    def get_company_fact_chart_data(cls, analysis_label, indicator, ticker):
        results = CompanyFactAnalysis.query.with_entities(
            CompanyFactAnalysis.ticker,
            CompanyFactAnalysis.val,
            CompanyFactAnalysis.frame
        ).filter(and_(
            CompanyFactAnalysis.ticker == ticker,
            CompanyFactAnalysis.analysis_label == analysis_label,
            CompanyFactAnalysis.fact_description == indicator
        )).all()
        return results
    

class StockPrice(db.Model, ModelUtils):
    __tablename__ = 'stock_prices'

    id = Column(Integer, primary_key=True)

    ticker = Column(String())
    date = Column(DateTime())
    open = Column(Numeric())
    close = Column(Numeric())
    high = Column(Numeric())
    volume = Column(Integer())
    adj_open = Column(Numeric())
    adj_close = Column(Numeric())
    adj_low = Column(Numeric())
    adj_high = Column(Numeric())
    adj_volume = Column(Integer())
    dividend = Column(Numeric())
    split = Column(Numeric())

    
    def __init__(self, **kwargs):
        super(StockPrice, self).__init__(**kwargs)

    @classmethod
    def find_by_identity(cls, ticker, start_date=None, end_date=None):
        results = StockPrice.query.filter(and_(
            StockPrice.ticker==ticker.upper(),
            StockPrice.date.between(start_date, end_date)
        )).all()

        return results

    @classmethod
    def backfill(cls, ticker, start_date='2000-01-01', end_date=None):
        print('Adding results')
        if end_date is None:
            end_date = datetime.today().strftime('%Y-%m-%d')
        rows = Tiingo().get_historical_prices(
            ticker, start_date, end_date)
        for row in rows:
            stock_price = StockPrice()
            stock_price.ticker = ticker.upper()
            for key, value in row.items():
                setattr(stock_price, key, value)
            stock_price.save()

    @classmethod
    def update(cls, ticker):
        end_date = datetime.today().strftime('%Y-%m-%d')
        ticker_dates = StockPrice.query.with_entities(
            StockPrice.date
        ).filter(
            StockPrice.ticker==ticker.upper()
        ).all()
        ticker_dates = [x.date for x in ticker_dates]
        print(ticker_dates, ticker)
        start_date = (max(ticker_dates) + timedelta(1)).strftime('%Y-%m-%d')
        rows = Tiingo().get_historical_prices(
            ticker, start_date, end_date)
        print(rows)
        for row in rows:
            print(row)
            if row['date'] in ticker_dates:
                continue
            stock_price = StockPrice()
            stock_price.ticker = ticker.upper()
            for key, value in row.items():
                setattr(stock_price, key, value)
            stock_price.save()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class BookLocation(db.Model, ModelUtils):

    __tablename__ = 'book_locations'

    id = Column(Integer, primary_key=True)

    title = Column(String())
    author = Column(String())
    locations = Column(String())

    def __init__(self, **kwargs):
        super(BookLocation, self).__init__(**kwargs)

    @classmethod
    def find_by_identity(cls, author, title):
        filters = []
        if author == '':
            book_locations = BookLocation.query.filter(
                BookLocation.title.ilike('%{}%'.format(title))).all()
        elif title == '':
            book_locations = BookLocation.query.filter(
                BookLocation.author.ilike('%{}%'.format(author))).all()
        else:
            book_locations = BookLocation.query.filter(and_(
                BookLocation.author.ilike('%{}%'.format(author)),
                BookLocation.title.ilike('%{}%'.format(title)))
            ).all()

        results = []
        for book_location in book_locations:
            locations = book_location.locations.split('|')
            
            for location in locations:
                loc_items = location.split('~')
                result = {
                    'lat': loc_items[0],
                    'long': loc_items[1],
                    'cnt': loc_items[2]
                }
                results.append(result)

        return results

    def delete(self):
        db.session.delete(self)
        db.session.commit()