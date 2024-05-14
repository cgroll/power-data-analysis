from datetime import datetime
import pandas as pd
import requests

from src.global_vars import GlobalVars

def get_indices(filter_value, region, resolution):
    """
    This function returns all available timestamps for a given time series.
    Each timestamp is a starting point in time for which several data points 
    can be retrieved. It behaves a bit like a pagination index.
    """
    
    base_url = GlobalVars.smard_api_base_url
    
    url = f"{base_url}/chart_data/{filter_value}/{region}/index_{resolution}.json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["timestamps"]
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

def query_series_data(filter_values, region, resolution, timestamp):
    """
    Query data for a list of time series IDs (filter_values), a given region,
    a given resolution and a given timestamp.
    """
    
    base_url = GlobalVars.smard_api_base_url
    
    data_list = []
    
    for filter_value in filter_values:
        url = f"{base_url}/chart_data/{filter_value}/{region}/{filter_value}_{region}_{resolution}_{timestamp}.json"
        response = requests.get(url)
        if response.status_code == 200:
            raw_data = response.json()["series"]
            
            time_list = []
            value_list = []

            for this_dt_point in raw_data:
                dt = tstamp_to_datetime(this_dt_point[0])
                time_list.append(dt)
                value_list.append(this_dt_point[1])

            df = pd.DataFrame(value_list, columns=['value'])
            df.insert(0, 'timestamp', time_list)
            df['series_id'] = filter_value

            data_list.append(df)
        else:
            print(f"Error: {response.status_code}, {response.text}")
    
    data_df = pd.concat(data_list)

    data_df_wide = data_df.pivot(index='timestamp', 
                                 columns='series_id', values='value')

    return data_df_wide

def query_full_series_data(series_id, region, freq):
    """
    Query all available data for a given series by iterating over all timestamp indices
    """

    timestamp_indices = get_indices(series_id, region, freq)

    data_list = []
    for this_index in timestamp_indices:
        series_data = query_series_data([series_id], 
                                        region, 
                                        freq, 
                                        this_index)
        data_list.append(series_data)

    data_df = pd.concat(data_list)

    return data_df

def tstamp_to_datetime(timestamp):

    # Convert milliseconds to seconds
    timestamp_sec = timestamp / 1000

    # Convert Unix timestamp to datetime object
    dt_utc = datetime.utcfromtimestamp(timestamp_sec)

    return dt_utc

def datetime_to_str(dt_object):

    dt_object.strftime("%Y-%m-%d %H:%M:%S")

def tstamp_to_str(timestamp):

    dt_object = tstamp_to_datetime(timestamp)
    return dt_object.strftime("%Y-%m-%d %H:%M:%S")

def get_day_of_year_consumption(consum_qh_df, this_id):
    
    day_of_year_consum = consum_qh_df.groupby(['day_of_month', 'month_of_year'])[this_id].mean() * 4
    day_of_year_consum = day_of_year_consum.reset_index()
    day_of_year_consum = day_of_year_consum.sort_values(['month_of_year', 'day_of_month'])

    year_date_str_list = []
    for this_day, this_month in zip(day_of_year_consum['day_of_month'], day_of_year_consum['month_of_year']):
        year_date_str = "{:02}".format(this_day) + "-" + "{:02}".format(this_month)
        year_date_str_list.append(year_date_str)

    day_of_year_consum['year_date'] = year_date_str_list
    day_of_year_consum = day_of_year_consum.drop(columns=['day_of_month', 'month_of_year'])
    day_of_year_consum = day_of_year_consum.set_index('year_date')

    return day_of_year_consum

def verify_resolution(this_res):

    known_res = ['hour', 'quarterhour', 'day', 'week', 'month', 'year']

    if not(this_res in known_res):
        raise ValueError(f'Unknown resolution: {this_res}')
    
def region_lookup(region_id):

    region_dict = {
        'DE': 'Deutschland',
        'AT': 'Österreich',
        'LU': 'Luxemburg',
        'DE-LU': 'Marktgebiet DE/LU (ab 01.10.2018)',
        'DE-AT-LU': 'Marktgebiet DE/AT/LU (bis 30.09.2018)',
        '50Hertz': 'Regelzone (DE): 50Hertz',
        'Amprion': 'Regelzone (DE): Amprion',
        'TenneT': 'Regelzone (DE): TenneT',
        'TransnetBW': 'Regelzone (DE): TransnetBW',
        'APG': 'Regelzone (AT): APG',
        'Creos': 'Regelzone (LU): Creos'
    }

    if not(region_id in region_dict.keys()):
        raise ValueError(f'Unknown region ID: {region_id}')

    return region_dict[region_id]

def series_id_lookup(series_id):

    series_id_dict= {
        1223: 'Stromerzeugung: Braunkohle',
        1224: 'Stromerzeugung: Kernenergie',
        1225: 'Stromerzeugung: Wind Offshore',
        1226: 'Stromerzeugung: Wasserkraft',
        1227: 'Stromerzeugung: Sonstige Konventionelle',
        1228: 'Stromerzeugung: Sonstige Erneuerbare',
        4066: 'Stromerzeugung: Biomasse',
        4067: 'Stromerzeugung: Wind Onshore',
        4068: 'Stromerzeugung: Photovoltaik',
        4069: 'Stromerzeugung: Steinkohle',
        4070: 'Stromerzeugung: Pumpspeicher',
        4071: 'Stromerzeugung: Erdgas',
        410: 'Stromverbrauch: Gesamt (Netzlast)',
        4359: 'Stromverbrauch: Residuallast',
        4387: 'Stromverbrauch: Pumpspeicher',
        4169: 'Marktpreis: Deutschland/Luxemburg',
        5078: 'Marktpreis: Anrainer DE/LU',
        4996: 'Marktpreis: Belgien',
        4997: 'Marktpreis: Norwegen 2',
        4170: 'Marktpreis: Österreich',
        252: 'Marktpreis: Dänemark 1',
        253: 'Marktpreis: Dänemark 2',
        254: 'Marktpreis: Frankreich',
        255: 'Marktpreis: Italien (Nord)',
        256: 'Marktpreis: Niederlande',
        257: 'Marktpreis: Polen',
        258: 'Marktpreis: Polen',
        259: 'Marktpreis: Schweiz',
        260: 'Marktpreis: Slowenien',
        261: 'Marktpreis: Tschechien',
        262: 'Marktpreis: Ungarn',
        3791: 'Prognostizierte Erzeugung: Offshore',
        123: 'Prognostizierte Erzeugung: Onshore',
        125: 'Prognostizierte Erzeugung: Photovoltaik',
        715: 'Prognostizierte Erzeugung: Sonstige',
        5097: 'Prognostizierte Erzeugung: Wind und Photovoltaik',
        122: 'Prognostizierte Erzeugung: Gesamt',
    }
        
    if not(series_id in series_id_dict.keys()):
        raise ValueError(f'Unknown series ID: {series_id}')
    
    return series_id_dict[series_id]

def get_selected_time_series_with_names():
    name_lookup_dict = {
        1225: 'wind_offshore',
        4067: 'wind_onshore',
        4068: 'pv',
        4359: 'residual_load',
        410: 'electricity_consumption',
        4169: 'market_price_de',
        5097: 'forecast_wind_pv'
    }
    # id_lookup_dict = {value: key for key, value in name_lookup_dict.items()}
    
    return name_lookup_dict
