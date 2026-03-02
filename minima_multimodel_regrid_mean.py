import numpy as np
import numpy.ma as ma
from scipy.interpolate import griddata
import os
import netCDF4 as nc

# Marco, 19.4. Si scrive un codice che prenda i file nc originali, ne estragga campo e coordinate,
# ne calcoli i minimi e li stampi nelle rispettive cartelle.
# Purtroppo non essendoci HadGEM3 e CESM2 su tintin i conti li dovrò fare a parte sul locale

# MARCO, 15.7. Si riavvia il codice solo per CNRM, per il quale si erano scelti gli indici sbagliati.
# index_path va cambiato!!

# Marco, 13.1.26. Si modifica il codice per stampare in output le composite sul campo di sea level pressure 
# senza calcolare l'anomalia, ma solo la media sui minimi di marzo.
# Le righe inutilizzate sono commentate per chiarezza.

# Marco, 14.1.26. Si correggono degli errori fatti ieri sera. L'obiettivo è calcolare correttamente:
# - la media dei minimi di marzo per SLP (non l'anomalia)
# - l'anomalia media dei minimi di marzo SLP
# entrambe regriddate su griglia GFDL. Siccome ieri era ero stanco, ho fatto un po' di confusione.
# Temo che ci sia una trattazione diversa da introdurre per CESM2; mi sa che avevo fatto le analisi sul locale, e con questo codice
# finisce per esserci un mismatch tra indici e serie temporale. 


# === Setup ===
models = ['GFDL', 'MRI', 'CNRM', 'MPI', 'CESM2', 'HadGEM3']
# variables = ['MLD', 'SST', 'SSS', 'SHF', 'SLP', 'SAT']  # Nomi delle variabili
# variables_CMIP =['mlotst', 'tos', 'sos', 'hfds', 'psl', 'tas'] # Nomi delle variabili CMIP
variables = ['SLP']  # Nomi delle variabili
variables_CMIP =['psl'] # Nomi delle variabili CMIP
ref_model = 'GFDL'  # Modello di riferimento per la griglia

base_path = '/home/buccellato/work_big/SPG/PCONTROL'
interp_root = f'{base_path}/Minima/March/Interpolated'

# Caricamento griglia e maschera del modello di riferimento
lat_ref = np.load(f'{base_path}/CODICI/MULTIMODEL/Coordinate/lat_{ref_model}_gr.npy')
lon_ref = np.load(f'{base_path}/CODICI/MULTIMODEL/Coordinate/lon_{ref_model}_gr.npy')
lon_ref_grid, lat_ref_grid = np.meshgrid(lon_ref, lat_ref)

grid_options = ['gr', 'gn']

for var1, var2 in zip(variables, variables_CMIP):
    print(f'\n📦 Variabile: {var1, var2}')

    for model in models:
        print(f'  🔁 Modello: {model}')

        dataset_found = False
        for grid in grid_options:
            nc_path = f"{base_path}/DATASETS/{model}/{var1}/pi{model}_{var1}_Datasets/{grid}/{var2}_{model}_piControl_{grid}.nc"

            if os.path.exists(nc_path):
                print(f"File trovato: {nc_path}")
                dataset_found = True
                break
            else:
                print(f"File non trovato: {nc_path}")
            

        # === Lettura NetCDF ===
        ds = nc.Dataset(nc_path)
        time_len = len(ds.dimensions['time'])  # Otteniamo la lunghezza della dimensione temporale
        ind_mar = [i + 2 for i in range(0, time_len, 12)]  # Marzo: offset 2 + passi annuali

        data = ds[var2][ind_mar, :, :]
        lat = ds['lat'][:]
        lon = ds['lon'][:]

        # === Percorsi legati a field ===
        index_path = f"{base_path}/CODICI/MULTIMODEL/MLD_TS/Output/MLD_{model}_minima_indexes.npy"
        output_path = f"{base_path}/CODICI/MULTIMODEL/Minima/March/{var1}/{var1}_{model}_composite_regridded_to_GFDL.npy"
        #output_path = f"{base_path}/CODICI/MULTIMODEL/Minima/March/{var1}/{var1}_{model}_minima_regridded_to_GFDL.npy"

        if model=='MPI':
            index_path = f"{base_path}/CODICI/{model}/MLD/Output/MLD_{model}_minima_indexes_500.npy"

        # === Caricamento indici ===
        indexes = np.load(index_path).tolist()

        if model=='CESM2':
            indexes = [i + 200 for i in indexes]

        data_shallow = data[indexes, :, :]
        
        # if var1=='MLD':
        #     # === Calcolo ===
        #     field = ma.mean(data_shallow, axis=0)
        if var1=='SLP':
            # === Calcolo ===
            field = ma.mean(data_shallow, axis=0)
        else:
            # === Calcolo Anomalia ===
            field = ma.mean(data_shallow, axis=0) - ma.mean(data, axis=0)

        # === Interpolazione ===
        # === Ricostruzione griglie modello ===
        lon_model_grid, lat_model_grid = np.meshgrid(lon, lat)

        # === Maschera valida per l'interpolazione ===
        valid_mask = ~ma.getmaskarray(field)
        valid_points = np.array([lon_model_grid[valid_mask], lat_model_grid[valid_mask]]).T
        valid_values = field[valid_mask]

        interp_data = griddata(valid_points, valid_values, (lon_ref_grid, lat_ref_grid), method='nearest')
        interp_data = ma.masked_invalid(interp_data)

        # === Salvataggio ===
        interp_dir = os.path.dirname(output_path)
        os.makedirs(interp_dir, exist_ok=True)  # Crea la directory se non esiste

        # Salva i dati interpolati
        interp_data.dump(output_path)
        print(f"    ✅ Salvataggio in {output_path}")