import sqlalchemy
import pandas as pd
from sqlalchemy import select, inspect

class ModelMixin:
    def __init__(self, database='finance_dwh') -> None:
        self.engine = self.create_engine(database)

    @classmethod
    def create_engine(cls, database='finance_dwh'):
        url_object = sqlalchemy.engine.URL.create(
            "postgresql+psycopg2",
            username="pguser",
            password="pgpass",
            host="localhost",
            database=database,
            port=5431
        )

        engine = sqlalchemy.create_engine(
            url_object)
        return engine
    
    @classmethod
    def query(cls, select_statement, to_df=False):
        engine = cls.create_engine()
        with engine.connect() as conn:
            if to_df:
                return pd.read_sql_query(
                    select_statement, con=engine)
            else:
                return conn.execute(
                    select_statement)
        
    @classmethod
    def all(cls, limit=None):
        select_statement = select(cls).limit(limit)
        return cls.query(select_statement)
    
    def create(self):
        exists = inspect(
            self.engine).has_table(self.__tablename__)
        if not exists:
            self.__table__.create(self.engine)

    def drop(self):
        exists = inspect(
            self.engine).has_table(self.__tablename__)
        if exists:
            self.__table__.drop(self.engine)

    def truncate(self):
        self.drop()
        self.create()

    def append(self, rows_to_add):
        insert_stmt = self.__table__.insert()
        with self.engine.begin() as conn:
            conn.execute(insert_stmt, rows_to_add)

    def write_truncate(self, rows_to_add, truncate_condition):
        delete_stmt = self.model.delete().where(
            truncate_condition)
        delete_stmt.execute()
        self.__table__.insert().execute(rows_to_add)
