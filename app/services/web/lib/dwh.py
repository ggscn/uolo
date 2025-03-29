import sqlalchemy
import pandas as pd
from sqlalchemy import text as sql_text

class DWHConnection:
    def __init__(self) -> None:
        """
        Set listen_addresses = '*' in postgresql.conf
        add line to pg_hba.conf to host        all         all          0.0.0.0/0           md5
        "Connection IP docker network inspect bridge -f '{{range .IPAM.Config}}{{.Gateway}}{{end}}'"
        """

        self.url_object = sqlalchemy.engine.URL.create(
            "postgresql+psycopg2",
            username="pguser",
            password="pgpass",
            host="172.17.0.1",
            database="finance_dwh",
            port=5431
        )
        self.engine = self.get_db_engine()
        
    def get_db_engine(self):
        engine = sqlalchemy.create_engine(
            self.url_object) 
        return engine

    def query(self, query_str):
        return pd.read_sql_query(
            sql=sql_text(query_str), con=self.engine.connect())