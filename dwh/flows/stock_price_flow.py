from prefect import flow
from lib.table import Table
from models.stock_price import StockPrice

@flow 
def get_stock_price():
    Table(StockPrice)

if __name__ == '__main__':
    get_stock_price()