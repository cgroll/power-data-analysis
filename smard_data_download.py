# %%
import requests
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pytz

base_url = "https://www.smard.de/app"

# Function to query indices data
def get_indices(filter_value, region, resolution):
    url = f"{base_url}/chart_data/{filter_value}/{region}/index_{resolution}.json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["timestamps"]
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

def query_series_data(filter_values, region, resolution, timestamp):
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

def add_time_metrics(df):
    
    berlin_tz = pytz.timezone('Europe/Berlin')
    
    dt_berlin = df['timestamp'].dt.tz_convert(berlin_tz)
    df['hour_of_day_berlin'] = dt_berlin.dt.hour
    df['date'] = df['timestamp'].dt.date
    df['day_of_month'] = df['timestamp'].dt.day
    df['day_of_year'] = df['timestamp'].dt.dayofyear
    df['week_of_year'] = df['timestamp'].dt.isocalendar().week
    df['month_of_year'] = df['timestamp'].dt.month
    df['year_month'] = df['timestamp'].dt.to_period('M')
    df['year'] = df['timestamp'].dt.year
    df['hour_of_day'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.day_name()
    df['15_minute_interval'] = df['timestamp'].dt.floor('15T')

    return df

# %% Power consumption

# 15 min data
# electricity_consumption_quarterhour_df = query_full_series_data(410, 'DE', 'quarterhour')

# electricity_consumption_quarterhour_df = electricity_consumption_quarterhour_df.reset_index().dropna()
# electricity_consumption_quarterhour_df.to_csv('energy_consumption_quarterhour.csv', index=False)

# %% wind offshore

name_lookup_dict = {
    1225: 'wind_offshore',
    4067: 'wind_onshore',
    4068: 'pv',
    4359: 'residual_load',
    410: 'electricity_consumption',
    4169: 'market_price_de',
    5097: 'forecast_wind_pv'
}

id_lookup_dict = {value: key for key, value in name_lookup_dict.items()}

id_list = list(name_lookup_dict.keys())
name_list = list(name_lookup_dict.values())

for this_id, this_name in zip(id_list, name_list):
    print(this_name)

    # this_data_quarterhour_df = query_full_series_data(this_id, 'DE', 'quarterhour')
    # this_data_quarterhour_df = this_data_quarterhour_df.reset_index().dropna()
    # this_data_quarterhour_df.to_csv(f'{this_name}_quarterhour.csv', index=False)

# %%

# Prognostizierte Erzeugung Wind und Photovoltaik: 5097
# wind offshore: 1225
# wind onshore: 4067
# PV: 4068
# Residuallast: 4359
# Marktpreis: Deutschland/Luxemburg: 4169

# realisierten Stromverbrauch bzw. der Netzlast, abzüglich der Erzeugung von Photovoltaik- und Windkraftanlagen. 
# Im Tagesverlauf kommt es, je nach Höhe der Einspeisung durch Erneuerbare, folglich zu Schwankungen der Residuallast.
# Ist sie Null oder gar negativ, konnte der Strombedarf komplett durch die Erzeugung aus Wind und Sonne gedeckt werden. 

# %% load data from disk

all_data_list = []

for this_name in name_list:
    this_data_quarterhour_df = pd.read_csv(f'{this_name}_quarterhour.csv')
    this_data_quarterhour_df['timestamp'] = pd.to_datetime(this_data_quarterhour_df['timestamp'], utc=True)
    this_data_quarterhour_df.set_index('timestamp', inplace=True)
    this_data_quarterhour_df.columns = [this_name]

    all_data_list.append(this_data_quarterhour_df)

data_qh_df = pd.concat(all_data_list, axis=1)
data_qh_df = data_qh_df.reset_index()
data_qh_df = add_time_metrics(data_qh_df)
data_qh_df

# %% load data from disk

consum_qh_df = pd.read_csv('energy_consumption_quarterhour.csv')
consum_qh_df['timestamp'] = pd.to_datetime(consum_qh_df['timestamp'], utc=True)
consum_qh_df.head(3)

# %% add time metadata

consum_qh_df = add_time_metrics(consum_qh_df)
consum_qh_df.tail(20)

# %% plot consumption over time

annual_consum = consum_qh_df.groupby('year')["410"].sum()
annual_consum = annual_consum.iloc[1:] # drop first partial year
annual_consum.plot(kind='bar')
plt.title('Annual energy consumption')
plt.show()

# %% plot average annual hourly consumption

annual_consum = consum_qh_df.groupby('year')["410"].mean() * 4
annual_consum = annual_consum.iloc[1:] # drop first partial year
annual_consum.plot(kind='bar')
plt.title('Average annual hourly energy consumption')
plt.show()

# %% plot average hourly consumption per month
ym_consum = consum_qh_df.groupby('year_month')["410"].mean() * 4
ym_consum.plot()
plt.title('Average hourly consumption per month over time')
plt.show()

# %% show calendar year seasonality

day_of_year_consum = get_day_of_year_consumption(consum_qh_df)
day_of_year_consum.plot()
plt.title('Average hourly consumption per calendar day')
plt.show()

# %% show extreme days

day_of_year_consum.sort_values("410").head(20)

day_of_year_consum.sort_values("410").tail(5)

# %% show only weekdays

weekday_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
weekday_consum = consum_qh_df.query('day_of_week in @weekday_list')

day_of_year_consum = get_day_of_year_consumption(weekday_consum)
day_of_year_consum.plot()
plt.title('Average hourly consumption per calendar day (weekdays only)')
plt.show()

# %% show only weekends

weekendday_list = ['Saturday', 'Sunday']
weekend_consum = consum_qh_df.query('day_of_week in @weekendday_list')

day_of_year_consum = get_day_of_year_consumption(weekend_consum)
day_of_year_consum.plot()
plt.title('Average hourly consumption per calendar day (weekends only)')
plt.show()

# %% show weekday pattern

avg_weekday_consumption = consum_qh_df.groupby('day_of_week')["410"].mean() * 4
weekday_sorting = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                   'Saturday', 'Sunday']
avg_weekday_consumption.loc[weekday_sorting].plot(kind='bar')
plt.title('Average hourly consumption per week day')
plt.show()

# %% show intra-day pattern

avg_intraday_consum = consum_qh_df.groupby('hour_of_day_berlin')["410"].mean() * 4
avg_intraday_consum.plot(kind='bar')
plt.title('Average intra-day hourly consumption')
plt.show()



# %% what is peak demand within a quarter-hour? / hour?

# %% how quickly can demand change?

sorted_consumption = consum_qh_df.sort_values('timestamp')["410"]
rel_change = (sorted_consumption.shift(1) - sorted_consumption)/sorted_consumption
rel_change.dropna().plot()


# %% how does this compare to renewable energy consumption?


# %% load PV data from disk

pv_qh_df = pd.read_csv('pv_quarterhour.csv')
pv_qh_df['timestamp'] = pd.to_datetime(pv_qh_df['timestamp'], utc=True)
#pv_qh_df = add_time_metrics(pv_qh_df)
pv_qh_df.head(3)

# %%



# %%

data_df[410].head(370).sort_values().head(30)

# %% group by week of 

cal_week = [dt.isocalendar().week for dt in data_df.index]
data_df['week_of_year'] = cal_week
data_df = data_df.dropna()

sns.boxplot(data=data_df, x='week_of_year', y=410)
plt.title('Annual seasonal patterns of energy consumption data')
plt.show()

# %%
data_df.resample('1w').mean().plot()

# %%

[tstamp_to_datetime(timestamp) for timestamp in consumption_indices]

# %%


# %%



# %%


planned_sources = series_data.drop(columns=[410, 4359, 4387])
planned_sources.plot()

x = planned_sources.index
y = np.cumsum(planned_sources, axis=1)

sns.set(style='whitegrid')
plt.stackplot(x, *y, labels=planned_sources.columns)
plt.legend(loc='upper left')
plt.title('Stacked Line Chart')
plt.xlabel('Month')
plt.ylabel('Values')
plt.show()

# %%

agg_sources = planned_sources.sum(axis=1)

agg_sources.plot()
series_data[410].plot()

# %%

#xx = agg_sources + series_data[4387] # + series_data[4359] 
#xx.plot()
series_data[410].plot()
#series_data[4359].plot()
series_data[4387].plot()

# %%

(agg_sources - series_data[410]).plot()


# %%

y

# %%

series_data.plot()

# %%

[series_id_lookup(this_id) for this_id in series_data.columns.values]


# %%
