import xarray as xr
import numpy as np
import os
import pandas as pd


# Marco, 20.6.25. In questo script si calcolano le serie temporali di dT, dS e dF su tutto il piControl, per tutti i modelli.

# Marco, 25.6.25. Si calcola separatamente l'anomalia anche per il MLD.

models = ['CESM2', 'HadGEM3', 'GFDL', 'MRI', 'CNRM', 'MPI']
base_dir = '/home/buccellato/work_big/SPG/PCONTROL/DATASETS/'
output_dir = '/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Bilanci_extended/Output/Serie temporali'
Y = 0
m = 0

# Si commenta temporaneamente
variables = {
    'SST': {'var_name': 'tos', 'folder': 'SST', 'suffix': 'SST'},
    'SSS': {'var_name': 'sos', 'folder': 'SSS', 'suffix': 'SSS'},
    'SHF': {'var_name': 'hfds', 'folder': 'SHF', 'suffix': 'SHF'}
}

# variables = {
#     'MLD': {'var_name': 'mlotst', 'folder': 'MLD', 'suffix': 'MLD'}
# }


for model in models:
    print(f"\n🔁 Processing model: {model}")
    
    for var_key, info in variables.items():
        print(f"  ➤ Processing variable: {var_key}")


        # Costruzione path
        fn_gr = os.path.join(base_dir, model, info['folder'], f'pi{model}_{info["suffix"]}_Datasets', 'gr', f'{info["var_name"]}_{model}_piControl_gr.nc')
        if not os.path.exists(fn_gr):
            print(f"    ❌ File not found: {fn_gr}")
            continue

        # Condizione speciale per CESM2
        if model == 'CESM2':
            Y = 2400
            m = 90
        else:
            Y = 0
            m = 0   
        
        print(Y, m)

        # Caricamento dati
        ds = xr.open_dataset(fn_gr, chunks={'time': 10})
        # ds = xr.decode_cf(ds)  # Decodifica tutte le coordinate tempo
        var = ds[info['var_name']][Y:, m:, :]


        # Coordinate convettive
        coord_base = '/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Bilanci_extended/Coord_conv_Labrador'
        lat_file = os.path.join(coord_base, f'lat_conv_{model}_gr.npy')
        lon_file = os.path.join(coord_base, f'lon_conv_{model}_gr.npy')

        if not os.path.exists(lat_file) or not os.path.exists(lon_file):
            print(f"    ❌ Coordinate non trovate per {model}")
            continue

        lat_conv = np.load(lat_file).tolist()
        lon_conv = np.load(lon_file).tolist()

        # Estrazione e media spaziale
        var_spatial_mean = var.isel(lat=lat_conv, lon=lon_conv).mean(dim=('lat', 'lon')).compute()
        print("var_spatial_mean shape:", var.shape)

        # if not np.issubdtype(var_spatial_mean['time'].dtype, np.datetime64):
        #     var_spatial_mean = var_spatial_mean.assign_coords(
        #         time=pd.to_datetime(var_spatial_mean['time'].values)
        #     )

        # Anomalia mensile (senza standardizzazione)
        var_monthly_mean = var_spatial_mean.groupby('time.month').mean('time')
        var_anom = var_spatial_mean.groupby('time.month') - var_monthly_mean

        # Salvataggio
        output_path = os.path.join(output_dir, var_key, f'piControl_{var_key}_anomalia_{model}.npy')
        np.save(output_path, var_anom.values)
        print(f"    ✅ Anomalie salvate in: {output_path}")
