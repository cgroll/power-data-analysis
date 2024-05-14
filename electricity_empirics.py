# %%
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pytz

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

# %%

data_qh_df['wind_pv'] = data_qh_df['wind_offshore'] + data_qh_df['wind_onshore'] + data_qh_df['pv']
data_qh_df['pct_residual_load'] = data_qh_df['residual_load'] / data_qh_df['electricity_consumption'] * 100
data_qh_df

# %%

# %% plot consumption over time

def plot_series_annual_agg(data_qh_df, series_name, drop_first=True):
    annual_consum = data_qh_df.groupby('year')[series_name].sum()
    if drop_first:
        annual_consum = annual_consum.iloc[1:] # drop first partial year
    annual_consum.plot(kind='bar')

def plot_series_annual_avg(data_qh_df, series_name, drop_first=True):
    annual_consum = data_qh_df.groupby('year')[series_name].mean() * 4
    if drop_first:
        annual_consum = annual_consum.iloc[1:] # drop first partial year
    annual_consum.plot(kind='bar')

def plot_series_avg(data_qh_df, series_name, groupby):
    annual_consum = data_qh_df.groupby(groupby)[series_name].mean() * 4
    annual_consum.plot(kind='bar')

    
# %%

plot_series_annual_agg(data_qh_df, 'electricity_consumption')
plt.title('Annual energy consumption')
plt.show()

# %%

annual_consum = data_qh_df.loc[:, ['wind_pv', 'electricity_consumption', 'residual_load', 'year']].groupby('year').sum()
annual_consum.plot(kind='bar')
plt.title('Consumption vs renewables')
plt.show()

# %%

annual_consum['pct_wind_pv'] = annual_consum['wind_pv'] / annual_consum['electricity_consumption'] * 100
annual_consum['pct_wind_pv'].plot(kind='bar')
plt.title('Percentage wind / pv power generation vs power consumption')
plt.show()

# %%

annual_consum['pct_wind_pv'] = annual_consum['wind_pv'] / annual_consum['electricity_consumption'] * 100
annual_consum['pct_wind_pv'].plot(kind='bar')
plt.title('Percentage wind / pv power generation vs power consumption')
plt.show()

# %% plot average annual hourly consumption

plot_series_annual_avg(data_qh_df, 'electricity_consumption')
plt.title('Average annual hourly energy consumption')
plt.show()

# %%

plot_series_annual_avg(data_qh_df, 'wind_pv')
plt.title('Average annual hourly energy generation from wind and pv')
plt.show()


# %%

year_month_elec_df = data_qh_df.groupby('year_month')['electricity_consumption'].mean() * 4
year_month_elec_df.plot()
plt.title('Average hourly consumption per month over time')
plt.show()

# %%

year_month_elec_df = data_qh_df.groupby('year_month')['wind_pv'].mean() * 4
year_month_elec_df.plot()
plt.title('Average hourly wind / pv generation per month over time')
plt.show()

# %%

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

# %%

day_of_year_consum = get_day_of_year_consumption(data_qh_df, 'electricity_consumption')
day_of_year_consum.plot()
plt.title('Average hourly consumption per calendar day')
plt.show()

# %%

week_year_elec_df = data_qh_df.groupby('week_of_year')['electricity_consumption'].mean() * 4
week_year_elec_df.plot()
plt.title('Average hourly consumption per week over time')
plt.show()

# %%

wind_pv_df = data_qh_df.groupby('week_of_year')['pv'].mean() * 4
wind_pv_df.plot()
plt.title('Average hourly pv generation per calendar week')
plt.show()

# %%

wind_pv_df = data_qh_df.groupby('week_of_year')['wind_offshore'].mean() * 4
wind_pv_df.plot()
plt.title('Average hourly wind generation (offshore) per calendar week')
plt.show()

# %%

wind_pv_df = data_qh_df.groupby('week_of_year')['wind_onshore'].mean() * 4
wind_pv_df.plot()
plt.title('Average hourly wind generation (onshore) per calendar week')
plt.show()


# %%

wind_pv_df = data_qh_df.groupby('hour_of_day')['pv'].mean() * 4
wind_pv_df.plot()
plt.title('Average hourly pv generation per daytime')
plt.show()

# %%

agg_data = data_qh_df.groupby('year_month')['residual_load'].max() * 4
agg_data.plot()
plt.title('Maximum scaled (hourly) residual load per year-month')
plt.show()

# %%

agg_data = data_qh_df.groupby('week_of_year')['residual_load'].max() * 4
agg_data.plot()
plt.title('Maximum scaled (hourly) residual load per week of year')
plt.show()

# %%

agg_data = data_qh_df.groupby('week_of_year')['pct_residual_load'].max()
agg_data.plot()
plt.title('Maximum scaled (hourly) residual load per week of year')
plt.show()


# %%

data_qh_df.set_index('timestamp')['pct_residual_load'].tail(2000).plot()
plt.title('Maximum percentage residual load')
plt.show()

# %%

wind_pv_df = data_qh_df.groupby('hour_of_day_berlin')['pct_residual_load'].mean()
wind_pv_df.plot()
plt.title('Average percentage residual load per daytime')
plt.show()

# %%

wind_pv_df = data_qh_df.groupby('hour_of_day_berlin')['pct_residual_load'].max()
wind_pv_df.plot()
plt.title('Maximum percentage residual load per daytime')
plt.show()


# %%

wind_pv_df = data_qh_df.groupby('date')['pct_residual_load'].max().tail(800)
wind_pv_df.plot()
plt.title('Maximum percentage residual load per day over time')
plt.show()
