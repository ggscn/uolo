from flask_app.app import make_celery
from lib.bigquery import BigQuery
from flask_app.blueprints.analysis.models import StockPrice



celery = make_celery()

@celery.task()
def backfill():
    tracked_tickers = [
        'BTU',
        'RIG',
        'AAPL',
        'ULBI'
    ]
    for ticker in tracked_tickers:
        print(ticker)
        StockPrice.backfill(ticker)




