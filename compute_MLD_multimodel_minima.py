import numpy as np
import os
import xarray as xr

# Marco, 25.6.25. In questo script si calcolano spot i valori multimodel di MLD durante la shallow convection e si standardizzano.

# Lista dei modelli
models = ['CESM2', 'HadGEM3', 'MPI', 'GFDL', 'MRI', 'CNRM']

# Directory base dei modelli
base_dir = '/home/buccellato/work_big/SPG/PCONTROL/DATASETS/'

Y = 0
m = 0

March_MLD_shallow = []
March_MLD_shallow_1_year_before = []
March_MLD_shallow_2_year_before = []

for model in models:
    print(f"\n🔁 Processing model: {model}")
    
    # Costruzione del path per il file MLD
    fn_gr = os.path.join(base_dir, model, 'MLD', f'pi{model}_MLD_Datasets', 'gr', f'mlotst_{model}_piControl_gr.nc')
    
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

    # Caricamento dei dati MLD
    ds = xr.open_dataset(fn_gr, chunks={'time': 10})
    var = ds['mlotst'][Y:, m:, :]

    # === Coordinate della regione convettiva ===
    coord_base = '/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Bilanci_extended/Coord_conv_Labrador'
    lat_file = os.path.join(coord_base, f'lat_conv_{model}_gr.npy')
    lon_file = os.path.join(coord_base, f'lon_conv_{model}_gr.npy')
    lat_idx = np.load(lat_file)
    lon_idx = np.load(lon_file)

    # === Indici degli anni con shallow convection ===
    if model == 'MPI':
        minima_indexes = np.load(f'/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/MLD_TS/Output/MLD_{model}_minima_indexes_500.npy')
    else:
        minima_indexes = np.load(f'/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/MLD_TS/Output/MLD_{model}_minima_indexes.npy')

    time_len = var.sizes['time']
    ind_mar = [i + 2 for i in range(0, time_len, 12)]
    March_MLD = var.isel(time=ind_mar, lat=lat_idx, lon=lon_idx).mean(dim=['lat', 'lon']).values

    # === Calcolo climatologia (media e std su tutta la serie) ===
    clim_mean = np.mean(March_MLD)
    clim_std = np.std(March_MLD)

    print(f"  ➤ Climatologia per {model}: media={clim_mean:.2f}, std={clim_std:.2f}")

    # === Calcolo anomalie standardizzate ===
    for idx in minima_indexes:
        if idx < 2 or idx >= len(March_MLD):
            continue  # evitare underflow
        z0 = (March_MLD[idx] - clim_mean) / clim_std
        z1 = (March_MLD[idx - 1] - clim_mean) / clim_std
        z2 = (March_MLD[idx - 2] - clim_mean) / clim_std

        March_MLD_shallow.append(z0)
        March_MLD_shallow_1_year_before.append(z1)
        March_MLD_shallow_2_year_before.append(z2)

# === Calcolo media multimodello delle anomalie ===
z0_mm_mean = np.nanmean(March_MLD_shallow)
z1_mm_mean = np.nanmean(March_MLD_shallow_1_year_before)
z2_mm_mean = np.nanmean(March_MLD_shallow_2_year_before)

print("\n📊 Risultati finali - Multimodel mean delle anomalie standardizzate di MLD (marzo):")
print(f"  🟢 Anno con shallow convection: {z0_mm_mean:.2f}")
print(f"  🔵 Un anno prima:               {z1_mm_mean:.2f}")
print(f"  🔵 Due anni prima:              {z2_mm_mean:.2f}")