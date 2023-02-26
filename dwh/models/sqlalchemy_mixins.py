import sqlalchemy
from sqlalchemy import select, inspect

class ModelMixin:
    def __init__(self) -> None:
        self.engine = self.create_engine()

    @classmethod
    def create_engine(cls):
        url_object = sqlalchemy.engine.URL.create(
            "postgresql+psycopg2",
            username="pguser",
            password="pgpass",
            host="localhost",
            database="finance_dwh",
        )

        engine = sqlalchemy.create_engine(
            url_object)
        return engine
    
    @classmethod
    def query(cls, select_statement):
        engine = cls.create_engine()
        with engine.connect() as conn:
            return conn.execute(select_statement)
        
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
