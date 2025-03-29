import resolve_imports
from dwh.lib.edgar import EdgarRequest
from dwh.models.insider_transaction import ReportingOwner
from prefect import flow, task
import pandas as pd

@task
def get_transaction_data():
    results = EdgarRequest().get_insider_transactions(2024,1).result()
    return results

@flow(name="update-insider-transactions")
def update_insider_transactions():
    transaction_data = get_transaction_data()
    reporting_owners = transaction_data['REPORTINGOWNER.tsv']

    df = pd.DataFrame(reporting_owners)
    df.rename(columns={x:x.lower() for x in df.columns}, inplace=True)
    print(df.columns)
    table = ReportingOwner()
    table.truncate()
    table.append(df.to_dict('records'))
    
if __name__ == '__main__':
    update_insider_transactions()