import xarray as xr
import numpy as np
import os

# Marco, 19.6.25. Si procede al calcolo dell'indice NAO usando le regioni delle Azzorre e di Reykjanes. L'indice calcolato è 
# il più stupido di tutti, ma forse il più immediato (standardizzazione della differenza tra le due regioni, i.e. standardizzazione dell'indice
# di Walker & Bliss, 1932). 

# Lista dei modelli
models = ['CESM2', 'HadGEM3', 'MPI', 'GFDL', 'MRI', 'CNRM']

# Directory base dei modelli
base_dir = '/home/buccellato/work_big/SPG/PCONTROL/DATASETS/'

output_dir = '/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Bilanci_extended/Output/Serie temporali/NAO'

for model in models:

    Y = 0
    
    # Costruisci il path al file SLP per il modello corrente
    fn_gn = os.path.join(base_dir, model, 'SLP', f'pi{model}_SLP_Datasets', 'gn', f'psl_{model}_piControl_gn.nc')
    fn_gr = os.path.join(base_dir, model, 'SLP', f'pi{model}_SLP_Datasets', 'gr', f'psl_{model}_piControl_gr.nc')

    if os.path.exists(fn_gn):
        fn = fn_gn
    elif os.path.exists(fn_gr):
        fn = fn_gr
    else:
        print(f"SLP file not found for model {model}. Skipping.")
        continue
    print(f"Processing model: {model}")

    if model == 'CESM2':
        Y = 2400
    
    ds = xr.open_dataset(fn)

    # Creazione della griglia di latitudine e longitudine
    lat = ds['lat'].values
    lon = ds['lon'].values

    print(f"{model} lat range: {ds['lat'].values.min()} to {ds['lat'].values.max()}")
    print(f"{model} lon range: {ds['lon'].values.min()} to {ds['lon'].values.max()}")


    # COORDINATE BOX (±1° attorno al punto centrale)
    box_Azzorre = {"lat_min": 37.0, "lat_max": 41.0, "lon_min": 332.0, "lon_max": 336.0}
    box_Rey = {"lat_min": 62.0, "lat_max": 66.0, "lon_min": 336.0, "lon_max": 340.0}

    # Seleziona le regioni usando condizioni sui limiti della box
    SLP_Azzorre_box = ds['psl'][Y:, :, :].sel(lat=slice(box_Azzorre["lat_min"], box_Azzorre["lat_max"]),
                                lon=slice(box_Azzorre["lon_min"], box_Azzorre["lon_max"])).mean(dim=['lat', 'lon'])

    SLP_Rey_box = ds['psl'][Y:, :, :].sel(lat=slice(box_Rey["lat_min"], box_Rey["lat_max"]),
                                lon=slice(box_Rey["lon_min"], box_Rey["lon_max"])).mean(dim=['lat', 'lon'])

    # Calcola la differenza tra le due regioni
    SLP_diff = SLP_Azzorre_box - SLP_Rey_box

    # Raggruppa per mese e normalizza
    SLP_diff_mean = SLP_diff.groupby('time.month').mean('time')
    SLP_diff_std = SLP_diff.groupby('time.month').std('time')  # std mensile
    SLP_diff_anom = SLP_diff.groupby('time.month') - SLP_diff_mean  # anomalia mensile
    NAO_index = SLP_diff_anom.groupby('time.month') / SLP_diff_std  # z-score mensile

    # Verifico che l'indice NAO sia coerente temporalmente con gli eventi di convezione interrotta
    mld_indexes_path = os.path.join(output_dir, model, 'MLD/Output/', f'MLD_{model}_minima_indexes.npy')
    if os.path.exists(mld_indexes_path):
        indexes = np.load(mld_indexes_path).tolist()
        selected_values = NAO_index.values[[x * 12 + 1 for x in indexes]]
        print(f"Mean NAO index for minima MLD months in {model}: {np.mean(selected_values)}")
    else:
        print(f"MLD minima indexes file not found for model {model}. Skipping mean calculation.")



    # Salvataggio
    np.save(os.path.join(output_dir, f'NAO_index_boxes_{model}_18.6.npy'), NAO_index.values)
    
    print(f"NAO index time series for {model} saved successfully.")







# # Carica il dataset con xarray
# fn = "/home/buccellato/work_big/SPG/PCONTROL/DATASETS/MRI/SLP/piMRI_SLP_Datasets/gn/psl_MRI_piControl_gn.nc"
# ds = xr.open_dataset(fn)

# # Creazione della griglia di latitudine e longitudine
# lat = ds['lat'].values
# lon = ds['lon'].values

# # COORDINATE BOX (±1° attorno al punto centrale)
# box_Azzorre = {"lat_min": 37.0, "lat_max": 41.0, "lon_min": 332.0, "lon_max": 336.0}
# box_Rey = {"lat_min": 62.0, "lat_max": 66.0, "lon_min": 336.0, "lon_max": 340.0}

# # Seleziona le regioni usando condizioni sui limiti della box
# SLP_Azzorre_box = ds['psl'].sel(lat=slice(box_Azzorre["lat_min"], box_Azzorre["lat_max"]),
#                                 lon=slice(box_Azzorre["lon_min"], box_Azzorre["lon_max"])).mean(dim=['lat', 'lon'])

# SLP_Rey_box = ds['psl'].sel(lat=slice(box_Rey["lat_min"], box_Rey["lat_max"]),
#                             lon=slice(box_Rey["lon_min"], box_Rey["lon_max"])).mean(dim=['lat', 'lon'])

# # Calcola la differenza tra le due regioni
# SLP_diff = SLP_Azzorre_box - SLP_Rey_box


# # Raggruppa per mese e normalizza
# SLP_diff_mean = SLP_diff.groupby('time.month').mean('time')
# SLP_diff_std = SLP_diff.groupby('time.month').std('time')  # std mensile
# SLP_diff_anom = SLP_diff.groupby('time.month') - SLP_diff_mean  # anomalia mensile
# NAO_index = SLP_diff_anom.groupby('time.month') / SLP_diff_std  # z-score mensile


# indexes = np.load('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MRI/MLD/Output/MLD_MRI_minima_indexes.npy').tolist()

# print(np.mean(NAO_index.values[[x * 12 + 1 for x in indexes]]))

# # # Separa mese per mese
# #np.save("NAO_index_MRI.npy", NAO_index.values)


