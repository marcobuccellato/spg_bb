import xarray as xr
import numpy as np
import os

# Marco, 16.7.25. Calcolo NAO DJFM.
# 
# Si procede al calcolo dell'indice NAO usando le regioni delle Azzorre e di Reykjanes. L'indice calcolato è 
# il più stupido di tutti, ma forse il più immediato (standardizzazione della differenza tra le due regioni, i.e. standardizzazione dell'indice
# di Walker & Bliss, 1932). 

# Lista dei modelli
models = ['CESM2', 'HadGEM3', 'MPI', 'GFDL', 'MRI', 'CNRM']

# Directory base dei modelli
base_dir = '/home/buccellato/work_big/SPG/PCONTROL/DATASETS/'

output_dir = '/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Bilanci_extended/Output/Serie temporali/NAO_DJFM'

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

    months_djfm = [12, 1, 2, 3]
    SLP_diff_djfm = SLP_diff.sel(time=SLP_diff['time.month'].isin(months_djfm))

    years = np.unique(SLP_diff_djfm['time.year'].values)

    nao_vals = []
    nao_years = []

    for year in years:
        if year == years[0]:
        # solo JFM di quell’anno
            sel = SLP_diff_djfm.sel(time=SLP_diff_djfm['time.month'].isin([1, 2, 3]))
            sel = sel.sel(time=sel['time.year'] == year)
        elif year == years[-1]:
            # solo dicembre di quell’anno
            sel = SLP_diff_djfm.sel(time=SLP_diff_djfm['time.month'] == 12)
            sel = sel.sel(time=sel['time.year'] == year)
        else:
            sel = SLP_diff_djfm.sel(time=(
                ((SLP_diff_djfm['time.year'] == year - 1) & (SLP_diff_djfm['time.month'] == 12)) |
                ((SLP_diff_djfm['time.year'] == year) & (SLP_diff_djfm['time.month'].isin([1, 2, 3])))
            ))
        if sel.time.size > 0:
            nao_vals.append(sel.mean().values)
            nao_years.append(year)


    # Converti in array xarray
    nao_index_raw = xr.DataArray(
        data=nao_vals,
        coords={"year": nao_years},
        dims="year"
    )


    # Standardizza su base intera serie
    NAO_index = (nao_index_raw - nao_index_raw.mean()) / nao_index_raw.std()

    # Verifico che l'indice NAO sia coerente temporalmente con gli eventi di convezione interrotta
    mld_indexes_path = os.path.join('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/MLD_TS/Output', f'MLD_{model}_minima_indexes.npy')
    
    if model == 'MPI':
        mld_indexes_path = os.path.join('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/MLD_TS/Output', f'MLD_{model}_minima_indexes_500.npy')   
    if os.path.exists(mld_indexes_path):
        indexes = np.load(mld_indexes_path).tolist()
        print(f"Mean NAO index for minima MLD months in {model}: {NAO_index[indexes].mean().values}")
    else:
        print(f"MLD minima indexes file not found for model {model}. Skipping mean calculation.")

    print(f"Shape of NAO index for {model}: {NAO_index.shape}")

    # Salvataggio
    np.save(os.path.join(output_dir, f'NAO_index_boxes_DJFM_{model}.npy'), NAO_index.values)
    
    print(f"NAO index time series for {model} saved successfully.")
