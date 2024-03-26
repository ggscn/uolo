from utils import retry
import requests
import pandas as pd


class GDELTSyncJob:
    def __init__(self) -> None:
        pass

    @retry(10, 10)
    def list_files(self):
        url = 'http://data.gdeltproject.org/gdeltv2/lastupdate.txt'
        response = requests.get(url)
        files = [x.split(' ')[2] for x in response.text.split('\n') if x != '']
        return files

    def get_lastest_url(self, schema_name='gkg'):
        url = None
        for file in self.list_files():
            if schema_name in file:
                url = file
        return url

    def get_schema(self, schema_name='gkg'):
        file_path = f'finance/dwh/lib/{schema_name}_schema.txt'
        with open(file_path,'r') as f:
            return [x.replace('\n','') for x in f.readlines()]

    @retry(10,10)
    def request(self, url):
        df = pd.read_csv(url, compression='zip',sep='\t')
        return df

    def pull_latest(self):
        url = self.get_lastest_url()
        columns = self.get_schema()
        df = self.request(url)
        df.columns = columns
        df.drop(columns=['counts','themes','locations','persons','organizations'])
        df['record_url'] = url
        return df.to_dict('records')


GDELTSyncJob().pull_latest()