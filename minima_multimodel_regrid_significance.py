import numpy as np
import numpy.ma as ma
from scipy.interpolate import griddata
from scipy.stats import ttest_ind
import os
import netCDF4 as nc

# Marco, 14.1.26. Si aggiornano le maschere di significatività per CESM2, per il quale c'era un mismatch indici-serie temporale, sia per p=0.1 che per p=0.05.

# === Setup ===
#models = ['CESM2', 'HadGEM3', 'GFDL', 'MRI', 'CNRM', 'MPI']
models = ['CESM2']

variables = ['MLD', 'SST', 'SSS', 'SHF', 'SLP', 'SAT']
variables_CMIP = ['mlotst', 'tos', 'sos', 'hfds', 'psl', 'tas']
ref_model = 'GFDL'

base_path = '/home/buccellato/work_big/SPG/PCONTROL'

# Griglia di riferimento
lat_ref = np.load(f'{base_path}/CODICI/MULTIMODEL/Coordinate/lat_{ref_model}_gr.npy')
lon_ref = np.load(f'{base_path}/CODICI/MULTIMODEL/Coordinate/lon_{ref_model}_gr.npy')
lon_ref_grid, lat_ref_grid = np.meshgrid(lon_ref, lat_ref)

grid_options = ['gr', 'gn']

for var1, var2 in zip(variables, variables_CMIP):
    print(f'\n📌 Variabile: {var1}')

    significance_masks = []

    for model in models:
        print(f'  🔁 Modello: {model}')

        dataset_found = False
        for grid in grid_options:
            nc_path = f"{base_path}/DATASETS/{model}/{var1}/pi{model}_{var1}_Datasets/{grid}/{var2}_{model}_piControl_{grid}.nc"
            if os.path.exists(nc_path):
                print(f"    ✅ File trovato: {nc_path}")
                dataset_found = True
                break
            else:
                print(f"    ⛔ File non trovato: {nc_path}")

        if not dataset_found:
            continue

        # === Caricamento dati ===
        ds = nc.Dataset(nc_path)
        time_len = len(ds.dimensions['time'])
        ind_mar = [i + 2 for i in range(0, time_len, 12)]

        data = ds[var2][ind_mar, :, :]
        lat = ds['lat'][:]
        lon = ds['lon'][:]

        # === Caricamento indici dei minimi ===
        index_path = f"{base_path}/CODICI/MULTIMODEL/MLD_TS/Output/MLD_{model}_minima_indexes.npy"
        if model == 'MPI':
            index_path = f"{base_path}/CODICI/MULTIMODEL/MLD_TS/Output/MLD_{model}_minima_indexes_500.npy"
        indexes = np.load(index_path).tolist()

        if model=='CESM2':
            indexes = [i + 200 for i in indexes]

        data_shallow = data[indexes, :, :]

        # === Calcolo significatività ===
        mask = ma.getmaskarray(ma.mean(data, axis=0))
        significant_mask = np.full(mask.shape, False)

        for i in range(data.shape[1]):
            for j in range(data.shape[2]):
                if not mask[i, j]:
                    sample1 = data_shallow[:, i, j].compressed()
                    sample2 = data[:, i, j].compressed()
                    if len(sample1) > 1 and len(sample2) > 1:
                        _, pval = ttest_ind(sample1, sample2, equal_var=False)
                        if pval < 0.05:  # Significatività al 95%
                            significant_mask[i, j] = True

        # === Interpolazione ===
        lon_model_grid, lat_model_grid = np.meshgrid(lon, lat)
        valid_points = np.array([lon_model_grid[~mask], lat_model_grid[~mask]]).T
        valid_values = significant_mask[~mask].astype(float)

        interp_significance = griddata(valid_points, valid_values,
                                       (lon_ref_grid, lat_ref_grid), method='nearest')
        interp_significance = np.round(interp_significance).astype(bool)

        significance_masks.append(interp_significance)

        # === Salvataggio della maschera di significatività === 
        os.makedirs(f"{base_path}/CODICI/MULTIMODEL/Minima/March/Significance/p_0.05/{var1}", exist_ok=True)
        output_path = f"{base_path}/CODICI/MULTIMODEL/Minima/March/Significance/p_0.05/{var1}/{var1}_{model}_significance_regridded_to_GFDL.npy"
        np.save(output_path, interp_significance)
        print(f"    ✅ Maschera di significatività salvata in {output_path}")

    # # === Unione finale ===
    # if significance_masks:
    #     common_mask = np.logical_and.reduce(significance_masks)

    #     # === Salvataggio ===
    #     output_path = f"{base_path}/CODICI/MULTIMODEL/Minima/March/Significance/{var1}_significance_common_mask_regridded_to_GFDL.npy"
    #     os.makedirs(os.path.dirname(output_path), exist_ok=True)
    #     common_mask.dump(output_path)
    #     print(f"✅ Maschera finale salvata in {output_path}")
    # else:
    #     print(f"⚠️ Nessuna maschera calcolata per {var1}")