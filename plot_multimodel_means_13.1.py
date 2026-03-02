import numpy as np
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import os
import matplotlib.patches as mpatches  # in cima al file, se non già importato

# Marco, 13.1.26. Si modifica il plot con le multimodel means in varie cose:


# === Configurazione ===
variables = ['MLD', 'SST', 'SSS', 'SLP', 'SHF', 'SAT']
models = ['CESM2', 'HadGEM3', 'GFDL', 'MRI', 'CNRM', 'MPI']  # Modelli da considerare
base_path = '/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Minima/March'

lat = np.load('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Coordinate/lat_GFDL_gr.npy')
lon = np.load('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Coordinate/lon_GFDL_gr.npy')

MLD_conv = np.load('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Climatologie/MLD/Grid_GFDL/MLD_conv_multimodel.npy')

# Coordinate e proiezione
lon_dx, lon_sx = 10, -69
lat_down, lat_up = 30, 80
proj = ccrs.LambertConformal(central_longitude=-30, central_latitude=58.0)
#proj = ccrs.Mollweide(central_longitude=-30)


n = 30
aoi = mpath.Path(
    list(zip(np.linspace(lon_sx, lon_dx, n), np.full(n, lat_up))) +
    list(zip(np.full(n, lon_dx), np.linspace(lat_up, lat_down, n))) +
    list(zip(np.linspace(lon_dx, lon_sx, n), np.full(n, lat_down))) +
    list(zip(np.full(n, lon_sx), np.linspace(lat_down, lat_up, n)))
)

# Funzione per caricare i dati multimodel mean
def load_multimodel_mean(variable):
    file_path = f"{base_path}/{variable}/{variable}_multimodel_mean.npy"
    if os.path.exists(file_path):
        return np.load(file_path, allow_pickle=True)
    else:
        print(f"⚠️ File non trovato: {file_path}")
        return None

# Funzione per creare il plot
def plot_multimodel_means():
    nrows, ncols = 2, 3  # 2 righe e 3 colonne
    fig, ax = plt.subplots(nrows, ncols, figsize=(16, 9), subplot_kw={'projection': proj})
    ax = ax.flatten()  # Appiattisci l'array di assi per un accesso più semplice

    plt.subplots_adjust(hspace=0.4, wspace=0.3)  # Aumenta lo spazio verticale e orizzontale tra i grafici

    for i, variable in enumerate(variables):
        data = load_multimodel_mean(variable)
        if data is not None:
            # Livelli e colormap (personalizzabili per ogni variabile)
            # Lettere per i pannelli
            panel_label = f"{chr(97 + i)})"  # 'a)', 'b)', ...
            ax[i].text(
                0.02, 0.98, panel_label, transform=ax[i].transAxes,
                fontsize=16, fontweight='semibold', va='top', ha='left', color='black', zorder=200
            )
            if variable == 'SST':  # Sea Surface Temperature
                levels, cmap = np.linspace(-2, 2, 9), 'coolwarm'
                cbar_title = r'$\Delta T$ (°C)'
            elif variable == 'MLD':  # Mixed Layer Depth
                levels, cmap = list(range(100, 1500, 50)), 'Blues'
                cbar_title = 'MLD (m)'
                # Cornice tratteggiata intorno al pannello MLD
                for spine in ax[i].spines.values():
                    spine.set_edgecolor('r')
                    spine.set_linewidth(2.5)
                    spine.set_linestyle('--')
            elif variable == 'SSS':  # Sea Surface Salinity
                levels, cmap = np.linspace(-0.5, 0.5, 11), 'PuOr_r'
                cbar_title = r'$\Delta S$ (psu)'
            elif variable == 'SHF':  # Surface Heat Flux
                levels, cmap = np.linspace(-200, 200, 9), 'bwr'
                cbar_title = r'$\Delta F$ (W/m²)'
            elif variable == 'SLP':  # Sea Level Pressure
                levels, cmap = np.linspace(-8, 8, 9), 'RdBu_r'
                cbar_title = r'$\Delta p$ (hPa)'
            elif variable == 'SAT':  # Surface Air Temperature
                levels, cmap = np.linspace(-4, 4, 9), 'RdYlBu_r'
                cbar_title = r'$\Delta T$ (°C)'
            else:
                levels, cmap = np.linspace(-1, 1, 11), 'viridis'  # Default

            cf = ax[i].contourf(lon, lat, data, levels=levels, cmap=cmap, transform=ccrs.PlateCarree(), extend='both')
            ax[i].contour(lon, lat, MLD_conv, colors='k', linewidths=0.7, linestyles='dashed', transform=ccrs.PlateCarree())

            if variable == 'SLP':    
                SLP_composite = np.load('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Minima/March/SLP/SLP_composite_multimodel_mean.npy')
                cs = ax[i].contour(lon, lat, SLP_composite, levels=np.arange(990, 1031, 2), colors='darkgrey', 
                                   linewidths=0.9, linestyles='-', transform=ccrs.PlateCarree())
                label_levels = np.arange(1000, 1015, 2)
                print(label_levels)
                ax[i].clabel(cs, levels=label_levels, inline=False, inline_spacing=3, fontsize=9, fmt='%d', colors='dimgrey', zorder=101)

            ax[i].set_title(variable, y=1.02)
            ax[i].coastlines('50m')
            ax[i].set_extent((lon_sx, lon_dx, lat_down, lat_up))
            #ax[i].set_boundary(aoi, transform=ccrs.PlateCarree())
            ax[i].add_feature(cfeature.LAND, zorder=100, color='k', edgecolor='k')

            # Aggiungi una colorbar accanto a ciascun grafico
            cbar = fig.colorbar(cf, ax=ax[i], orientation='vertical', shrink=0.7, pad=0.07)
            cbar.ax.set_title(cbar_title, fontsize=10)

        else:
            ax[i].set_title(f"{variable} (No Data)")
            ax[i].axis('off')

    # Disattiva eventuali assi vuoti
    for i in range(len(variables), len(ax)):
        ax[i].axis('off')

    # Ottimizza il layout
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    # Titolo generale
    plt.suptitle("Multimodel mean anomalies associated to March shallow convection configurations", fontsize=18, y=0.98)

    # Salvataggio del grafico
    save_dir = f"{base_path}/Figures"
    os.makedirs(save_dir, exist_ok=True)  # Crea la directory se non esiste
    save_file = f"{save_dir}/multimodel_means_13.1.png"
    plt.savefig(save_file, dpi=200)
    print(f"✅ Grafico salvato in: {save_file}")
    plt.close()

# Esegui il plot
if __name__ == "__main__":
    plot_multimodel_means()