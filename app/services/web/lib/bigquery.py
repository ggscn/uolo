import os
from flask import current_app
from google.oauth2 import service_account
from google.cloud import bigquery

#https://blog.gdeltproject.org/google-bigquery-3-5m-books-sample-queries/

class BigQuery:
    def __init__(self):
        self.bq_client = self.get_client()

    def get_client(self):
        credentials = service_account.Credentials.from_service_account_file(
            current_app.config.get('SERVICE_ACCOUNT_PATH'))
        
        client = bigquery.Client(
             project='fyllo-237201', credentials=credentials)

        return client


    @classmethod
    def get_query_str(cls, query_name):
        query_str_path = '{}/{}/{}.sql'.format(
            os.path.dirname(os.path.abspath(__file__)), 'queries', query_name)
        
        with open(query_str_path, 'r') as f:
            query_str = f.read()

        return query_str


    def query(self, query_str):
        query_result = self.bq_client.query(
            query_str).result()
        
        cols = [x.name for x in query_result.schema]
        rows = [{c: r[i] for i, c in enumerate(cols)} for r in query_result]
        return rows
