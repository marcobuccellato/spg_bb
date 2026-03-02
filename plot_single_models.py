import numpy as np
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import os
import matplotlib.patches as mpatches  # in cima al file, se non già importato

# Marco, 13.1.26. In questo grafico le mappe vengono stampate singolarmente per ogni modello.

# === Configurazione ===
variables = ['MLD', 'SST', 'SSS', 'SLP', 'SHF', 'SAT']
models = ['CESM2', 'HadGEM3', 'GFDL', 'MRI', 'CNRM', 'MPI']  # Modelli da considerare
model_name = ['CESM2', 'HadGEM3-GC3.1-MM', 'GFDL-CM4', 'MRI-ESM2.0', 'CNRM-CM6-1-HR', 'MPI-ESM1.2']
base_path = '/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Minima/March'

lat = np.load('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Coordinate/lat_GFDL_gr.npy')
lon = np.load('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Coordinate/lon_GFDL_gr.npy')

# Creazione della griglia 2D di latitudine e longitudine
lon_grid, lat_grid = np.meshgrid(lon, lat)

# Funzione per identificare la regione convettiva
def boolean_converter_a(array):

    # Applicazione delle condizioni
    lat_condition = (lat_grid > 50) & (lat_grid < 65)
    lon_condition = (lon_grid > 295) & (lon_grid < 340)  # Convertito in gradi negativi per lon
    Swdom = lat_condition & lon_condition

    return (array > 1000) & Swdom


# Coordinate e proiezione
lon_dx, lon_sx = 10, -69
lat_down, lat_up = 30, 80
proj = ccrs.LambertConformal(central_longitude=-30, central_latitude=58.0)

# Funzione per caricare i dati multimodel mean
def load_multimodel_mean(variable, model):
    file_path = f"{base_path}/{variable}/{variable}_{model}_minima_regridded_to_GFDL.npy"
    if os.path.exists(file_path):
        return np.load(file_path, allow_pickle=True)
    else:
        print(f"⚠️ File non trovato: {file_path}")
        return None

# Funzione per creare il plot
def plot_multimodel_means():
    nrows, ncols = 2, 3  # 2 righe e 3 colonne

    for j, model in enumerate(models):
        # Si estrae la regione convettiva modello per modello     
        MLD_conv = boolean_converter_a(np.load(f'/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Climatologie/MLD/Grid_GFDL/MLD_{model}_regridded_to_GFDL.npy', allow_pickle=True))
        fig, ax = plt.subplots(nrows, ncols, figsize=(16, 9), subplot_kw={'projection': proj})
        ax = ax.flatten()  # Appiattisci l'array di assi per un accesso più semplice
        plt.subplots_adjust(hspace=0.4, wspace=0.3)  # Aumenta lo spazio verticale e orizzontale tra i grafici

        for i, variable in enumerate(variables):
            data = load_multimodel_mean(variable, model)
            
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
                    levels, cmap = np.linspace(250, 1250, 21), 'Blues'
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

                    data = data * 0.01  # Converti da Pa a hPa

                    SLP_composite = np.load(f'/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Minima/March/SLP/SLP_{model}_composite_regridded_to_GFDL.npy', allow_pickle=True)*0.01
                    cs = ax[i].contour(lon, lat, SLP_composite, levels=np.arange(990, 1031, 2), colors='darkgrey', linewidths=0.9, linestyles='-', transform=ccrs.PlateCarree())
                    label_levels = np.arange(1000, 1015, 2)
                    ax[i].clabel(cs, levels=label_levels, inline=False, inline_spacing=3, fontsize=9, fmt='%d', colors='dimgrey', zorder=101)

                elif variable == 'SAT':  # Surface Air Temperature
                    levels, cmap = np.linspace(-4, 4, 9), 'RdYlBu_r'
                    cbar_title = r'$\Delta T$ (°C)'
                else:
                    levels, cmap = np.linspace(-1, 1, 11), 'viridis'  # Default

                cf = ax[i].contourf(lon, lat, data, levels=levels, cmap=cmap, transform=ccrs.PlateCarree(), extend='both')
                ax[i].contour(lon, lat, MLD_conv, colors='k', linewidths=0.7, linestyles='dashed', transform=ccrs.PlateCarree())
                ax[i].set_title(variable)
                ax[i].coastlines('50m')
                ax[i].set_extent((lon_sx, lon_dx, lat_down, lat_up))
                ax[i].add_feature(cfeature.LAND, zorder=100, color='k', edgecolor='k')

                # Aggiungi una colorbar accanto a ciascun grafico
                cbar = fig.colorbar(cf, ax=ax[i], orientation='vertical', shrink=0.7, pad=0.07)  # Ridotto shrink
                cbar.ax.set_title(cbar_title, fontsize=10)

                # === SOVRAPPONI LA MASCHERA DI SIGNIFICATIVITÀ ===
                model_mask_path = f"{base_path}/Significance/p_0.1/{variable}/{variable}_{model}_significance_regridded_to_GFDL.npy"
                if os.path.exists(model_mask_path):
                    model_mask = np.load(model_mask_path)
                    print(f"File maschera trovato per {model}, {variable}")
                else:
                    print(f"⚠️  Maschera mancante per {model}: {model_mask_path}")

                if model_mask is not None and model_mask.any():

                # Si sovrappone la maschera di significatività simile a quella fatta per l'altro paper.
                    step = 2
                    lat_ds = lat[::step]
                    lon_ds = lon[::step]
                    sig_mask_ds = model_mask[::step, ::step]
                    sig_indices = np.where(sig_mask_ds)
                    lat_sig = lat_ds[sig_indices[0]]
                    lon_sig = lon_ds[sig_indices[1]]
                    ax[i].scatter(lon_sig, lat_sig, s=8, color='black', alpha=0.1, transform=ccrs.PlateCarree(), marker='o')

                    #ax[i].contourf(lon, lat, common_mask, levels=[0.5, 1], colors='none',
                    #               hatches=['///'], transform=ccrs.PlateCarree())
                
                else:
                    print(f"⛔ Nessuna maschera trovata per {variable}")
             
            else:
                ax[i].set_title(f"{variable} (No Data)")
                ax[i].axis('off')

        # Disattiva eventuali assi vuoti
        for i in range(len(variables), len(ax)):
            ax[i].axis('off')

        # Ottimizza il layout
        plt.tight_layout(rect=[0, 0, 1, 0.95])

        # Titolo generale
        plt.suptitle(f"{model_name[j]} mean anomalies associated to March shallow convection configurations", fontsize=18, y=0.98)

        # Salvataggio del grafico
        save_dir = f"{base_path}/Figures/Single_models_multivariate"
        os.makedirs(save_dir, exist_ok=True)  # Crea la directory se non esiste
        save_file = f"{save_dir}/{model}_composites_significance_0.1_13.1.26.png"
        plt.savefig(save_file, dpi=200)
        print(f"✅ Grafico salvato in: {save_file}")
        plt.close()

# Esegui il plot
if __name__ == "__main__":
    plot_multimodel_means()