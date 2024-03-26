import eurostat
import datetime
import resolve_imports
from dwh.models.lng_consumption import LNGConsumptionEU
from prefect import flow, task
import pandas as pd


energy_balance_types = {
    'IPRD': 'Indigenous production',
    'TOS': 'Transfer from other sources',
    'IMP': 'Imports',
    'EXP': 'Exports',
    'STK_CHG_CG': 'Change in stock - cushion gas',
    'STK_CHG_MG': 'Stock changes - as defined in MOS GAS',
    'INTMARB': 'International maritime bunkers',
    'IC_OBS': 'Inland consumption - observed',
    'IC_CAL_MG': 'Inland consumption - calculated as defined in MOS GAS',
    'TI_EHG_MAP': 'Transformation input - electricity and heat generation - main activity producers',
    'DL': 'Distributed losses',
    'VENT': 'Vented',
    'FLARE': 'Flare',
    'FC_IND': 'Final consumption - industry sector',
    'FC_OTH': 'Final consumpyion - other sectors',
    'STATDIFF': 'Statistical differences'
}


def get_energy_type(energy_balance):
    return energy_balance_types[energy_balance]

@flow(name='update-lng-consumption')
def update_consumption_data():
    df = eurostat.get_data_df('nrg_cb_gasm')
    date_columns = [
        col for col in df.columns if isinstance(col, datetime.datetime) or 
        (isinstance(col, str) and pd.to_datetime(col, format='%Y-%m', errors='coerce') is not pd.NaT)]

    df = df.melt(
        id_vars=[col for col in df.columns if col not in date_columns], 
        value_vars=date_columns, 
        var_name='Date', 
        value_name='Value'
    )
    df.rename(columns={
        'nrg_bal': 'energy_balance', 
        'siec': 'product_classification', 
        'geo\\TIME_PERIOD': 'country_code', 
        'Date': 'time_period', 
        'Value': 'amount', 
    }, inplace=True)
    df['energy_balance_type'] = df['energy_balance'].apply(lambda x: get_energy_type(x))
    table = LNGConsumptionEU()
    table.truncate()
    table.append(df.to_dict('records'))

if __name__ == '__main__':
    update_consumption_data()