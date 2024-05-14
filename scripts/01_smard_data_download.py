# %%
import os

from src.path import ProjPaths
from src.smard_api_utils import query_full_series_data, get_selected_time_series_with_names

# %% data download

data_path = str(ProjPaths.raw_data_path)

# Residual load:
# realisierten Stromverbrauch bzw. der Netzlast, abzüglich der Erzeugung von Photovoltaik- und Windkraftanlagen. 
# Im Tagesverlauf kommt es, je nach Höhe der Einspeisung durch Erneuerbare, folglich zu Schwankungen der Residuallast.
# Ist sie Null oder gar negativ, konnte der Strombedarf komplett durch die Erzeugung aus Wind und Sonne gedeckt werden. 

name_lookup_dict = get_selected_time_series_with_names()

id_list = list(name_lookup_dict.keys())
name_list = list(name_lookup_dict.values())
    
for this_id, this_name in zip(id_list, name_list):
    print(f'Data download started for {this_name}')
    
    fpath = os.path.join(data_path, f'{this_name}_quarterhour.csv')

    this_data_quarterhour_df = query_full_series_data(this_id, 'DE', 'quarterhour')
    this_data_quarterhour_df = this_data_quarterhour_df.reset_index().dropna()
    this_data_quarterhour_df.to_csv(fpath, index=False)


