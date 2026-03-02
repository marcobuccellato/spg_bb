import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.path as mpath
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.ticker import ScalarFormatter
import os

# Marco, 22.4. Occhio che la multimodel mean SLP viene salvata riscalata in output, a differenza di quelle importate
# in input. 

# Marco, 13.1.26. Anche qui si modifica il codice calcolando e plottando le composite sul campo SLP (non anomalia).

# Marco, 14.1.26. Si correggono degli errori fatti ieri sera, vedi file minima_multimodel_regrid_mean.py.

# === Configurazione ===
models = ['GFDL', 'MRI', 'CNRM', 'MPI', 'CESM2', 'HadGEM3']
# variables = ['MLD', 'SST', 'SSS', 'SHF', 'SLP', 'SAT']
variables = ['SLP']
base_path = '/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Minima/March'

lat = np.load('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Coordinate/lat_GFDL_gr.npy')
lon = np.load('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Coordinate/lon_GFDL_gr.npy')

# Coordinate e proiezione
lon_dx, lon_sx = 10, -69
lat_down, lat_up = 30, 80
proj = ccrs.LambertConformal(central_longitude=-30, central_latitude=58.0)

# Funzione per caricare i dati
def load_data(variable, model):
    file_path = f"{base_path}/{variable}/{variable}_{model}_minima_regridded_to_GFDL.npy"
    #file_path = f"{base_path}/{variable}/{variable}_{model}_composite_regridded_to_GFDL.npy"

    if os.path.exists(file_path):
        return np.load(file_path, allow_pickle=True)
    else:
        print(f"⚠️ File non trovato: {file_path}")
        return None

# Funzione per creare il plot
def plot_variable(variable):
    fig, ax = plt.subplots(1, len(models) + 1, figsize=(15, 5), subplot_kw={'projection': proj})
    all_data = []

    # Livelli e colormap (personalizzabili per ogni variabile)
    if variable == 'MLD':  # Mixed Layer Depth
        levels, cmap = np.linspace(250, 1250, 21), 'Blues'
    elif variable == 'SST':  # Sea Surface Temperature
        levels, cmap = np.linspace(-3, 3, 13), 'coolwarm'
    elif variable == 'SSS':  # Sea Surface Salinity
        levels, cmap = np.linspace(-0.6, 0.6, 13), 'PuOr_r'
    elif variable == 'SHF':  # Surface Heat Flux
        levels, cmap = np.linspace(-200, 200, 9), 'bwr'
    elif variable == 'SLP':  # Sea Level Pressure
        levels, cmap = np.linspace(-10, 10, 11), 'RdBu_r'
        # levels = np.arange(990, 1031, 5)
        # cmap = 'viridis'  # o cividis
        k = 0.01 # Fattore di conversione da Pa a hPa 
    elif variable == 'SAT':  # Surface Air Temperature
        levels, cmap = np.linspace(-6, 6, 13), 'RdYlBu_r'
    else:
        levels, cmap = np.linspace(-1, 1, 11), 'viridis'  # Default

    for i, model in enumerate(models):
        data = load_data(variable, model)
        if data is not None:
            if variable == 'SLP':  # Applica il fattore di conversione
                data *= k
            all_data.append(data)
            cf = ax[i].contourf(lon, lat, data, levels=levels, cmap=cmap, transform=ccrs.PlateCarree(), extend='both')
            ax[i].set_title(f"{model}")
            ax[i].coastlines('50m')
            ax[i].set_extent((lon_sx, lon_dx, lat_down, lat_up))
            ax[i].add_feature(cfeature.LAND, zorder=100, color='k', edgecolor='k')
        else:
            ax[i].set_title(f"{model} (No Data)")
            ax[i].axis('off')

    # Calcolo della multimodel mean
    if all_data:
        multimodel_mean = np.mean(all_data, axis=0)
        cf = ax[-1].contourf(lon, lat, multimodel_mean, levels=levels, cmap=cmap, transform=ccrs.PlateCarree(), extend='both')
        ax[-1].set_title("Multimodel Mean")
        ax[-1].coastlines('50m')
        ax[-1].set_extent((lon_sx, lon_dx, lat_down, lat_up))
        ax[-1].add_feature(cfeature.LAND, zorder=100, color='k', edgecolor='k')
        mean_save_file = f"{base_path}/{variable}/{variable}_multimodel_mean.npy"
        # mean_save_file = f"{base_path}/{variable}/{variable}_composite_multimodel_mean.npy"
        np.save(mean_save_file, multimodel_mean)
        print(f"✅ Multimodel mean salvata in: {mean_save_file}")

    else:
        ax[-1].set_title("Multimodel Mean (No Data)")
        ax[-1].axis('off')

    # Colorbar
    cbar_ax = fig.add_axes([0.93, 0.15, 0.02, 0.7])
    cbar = fig.colorbar(cf, cax=cbar_ax, orientation='vertical')
    #cbar.ax.set_title(f"$\Delta {variable}$", fontsize=10)
    cbar.ax.set_title(f"${variable}$", fontsize=10)
    cbar.ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    cbar.ax.yaxis.offsetText.set_fontsize(10)

    # Titolo generale
    plt.suptitle(f"Mappe per {variable}", y=0.94)

    # Salvataggio del grafico
    save_dir = f"{base_path}/Figures/{variable}"
    os.makedirs(save_dir, exist_ok=True)  # Crea la directory se non esiste
    save_file = f"{save_dir}/{variable}_multimodel_maps.png"
    #save_file = f"{save_dir}/{variable}_composite_multimodel_maps.png"
    plt.savefig(save_file, dpi=200)
    print(f"✅ Grafico salvato in: {save_file}")
    plt.close()

# Genera i plot per tutte le variabili
for variable in variables:
    print(f"📊 Generazione plot per {variable}...")
    plot_variable(variable)