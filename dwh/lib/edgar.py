import requests
import zipfile
import io
import csv
from pathlib import Path

class EdgarRequest():
    def __init__(self) -> None:
        self.base_url_api = 'https://data.sec.gov/api'
        self.base_url_bulk = 'https://www.sec.gov/files'
        self.base_url_legacy = "https://www.sec.gov/Archives"
        self.user_agent = "Personal Use Greg pguser@fastmail.com"
        self.tmp_directory = Path.home() / 'downloads'

    def get_company_facts(self, cik):
        cik = str(cik).zfill(10)
        
        headers = {
            'User-Agent': self.user_agent,
            'Host': 'data.sec.gov'
        }

        url = f'{self.base_url_api}/xbrl/companyfacts/CIK{cik}.json'

        response = self.do_request(
            url, headers)

        return EdgarCompanyFactResponse(response, cik)

    def get_insider_transactions(self, year=None, quarter=None):
        """Returns cleaned result of bulk insider transaction file

        Example:
        result = EdgarRequest().get_insider_transactions(2024,1).result()
        print(result['REPORTINGOWNER.tsv'])
        """
        headers = { 
            'User-Agent' : self.user_agent,
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        }
        tmp_location = self.tmp_directory / f'insider_tx_{year}q{quarter}'
        endpoint = f'{year}q{quarter}_form345.zip'
        url = f'{self.base_url_bulk}/structureddata/data/insider-transactions-data-sets/{endpoint}'
        
        response = self.do_request(
            url, headers)
        
        zfile = zipfile.ZipFile(
            io.BytesIO(response.content))
        zfile.extractall(tmp_location)
        return EdgarBulkInsiderTransactionResponse(tmp_location)

    def get_company_tickers(self):
        headers = {
            'User-Agent': self.user_agent,
            'Host': 'www.sec.gov'
        }
        url = 'https://www.sec.gov/files/company_tickers_exchange.json'
        response = self.do_request(
            url, headers)

        return EdgarCompanyTickerResponse(response)

    def do_request(self, url, headers):

        response = requests.get(
            url, headers=headers)
        return response

class EdgarBulkInsiderTransactionResponse():
    def __init__(self, response_location) -> None:
        self.response_location = response_location
        self.response_files = [
            'DERIV_HOLDING.tsv',
            'DERIV_TRANS.tsv',
            'NONDERIV_HOLDING.tsv',
            'NONDERIV_TRANS.tsv',
            'OWNER_SIGNATURE.tsv',
            'REPORTINGOWNER.tsv',
            'SUBMISSION.tsv'
        ]

    def parse_response_files(self):
        result = {}
        for response_file in self.response_files:
            with open(self.response_location / response_file, 'r') as f:
                rows = csv.reader(f, delimiter="\t", quotechar='"')
                columns = next(rows)
                result[response_file] = [{col: row[i] for i, col in 
                    enumerate(columns)} for row in rows]
        return result

    def result(self):
        return self.parse_response_files()

class EdgarCompanyTickerResponse():
    def __init__(self, api_response) -> None:
        self.api_response = api_response
        self.validate_response_data()

    def validate_response_data(self):
        self.api_response = self.api_response.json()

    def transform(self):
        data = [{
            field: val for field, val in zip(
                self.api_response['fields'], x)} 
                    for x in self.api_response['data']]
        return data

    def results(self):
        return self.transform()

class EdgarCompanyFactResponse():
    def __init__(self, api_response, cik) -> None:
        self.api_response = api_response
        self.validate_response_data()

    def validate_response_data(self):
        try:
            self.api_response = self.api_response.json()
            if (
                'us-gaap' not in self.api_response['facts'] and 
                'ifrs-full' not in self.api_response['facts']
            ):
                raise Exception(self.api_response['facts'].keys())
        except:
            self.api_response = None

    def validate_int(self, val):
        val = int(val)
        if val.bit_length() > 64:
            val = None
        return val

    def transform(self, **kwargs):
        data = []
        for rule_set, facts in self.api_response['facts'].items():
            for description, units in facts.items():
                for currency, entries in units['units'].items():
                    data.extend([{
                        'description': description,
                        'rule_set': rule_set,
                        'currency': currency,
                        'end': entry['end'],
                        'val': self.validate_int(entry['val']),
                        'fy': entry['fy'],
                        'fp': entry['fp'],
                        'form': entry['form'],
                        'accn': entry['accn'],
                        'frame': entry.get('frame', None),
                        'filed': entry.get('filed', None),
                        **kwargs
                    } for entry in entries])
        return data

    def result(self, **kwargs):
        if self.api_response is None:
            return None
        return self.transform(**kwargs)