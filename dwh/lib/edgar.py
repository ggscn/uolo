import requests
import zipfile
import io

class EdgarRequest():
    def __init__(self) -> None:
        self.base_url_api = 'https://data.sec.gov/api'
        self.base_url_legacy = "https://www.sec.gov/Archives"
        self.user_agent = "Personal Use Greg pguser@fastmail.com"

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

    def download_index(self):
        headers = { 
            'User-Agent' : self.user_agent,
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        }
        year = '2022'
        quarter = 'QTR3'
        endpoint = f'edgar/full-index/{year}/{quarter}/master.zip'

        response = self.do_request(url)

        zfile = zipfile.ZipFile(io.BytesIO(response.content))
        zfile.extractall("/home/pguser/downloads")

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

    def retrieve_facts(self):
        rule_sets = ['us-gaap', 'ifrs-full']
        for rule_set in rule_sets:
            if rule_set in self.api_response['facts']:
                return rule_set, self.api_response['facts'][rule_set]

    def transform(self, **kwargs):
        data = []
        rule_set, facts = self.retrieve_facts()
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