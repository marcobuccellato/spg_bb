import numpy as np
import netCDF4 as nc
import numpy.ma as ma
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import matplotlib.path as mpath
from matplotlib.ticker import ScalarFormatter

# Marco, 12.1.26. Si stampano vicine l'una all'altra le cliamtologie di MLD da datasets differenti.
# In particolare, in questo caso di mettono vicine le climatologie multimodel, le osservazioni LOPS e la rianalisi ORAS5 insieme 
# a quelle dei modelli uno a uno.

# === Configurazione ===

# Percorsi dei file .npy 
# MULTIMODEL MEAN
path_mld_multimodel_mean = '/Users/marcobuccellato/Documents/Dottorato/2025_2026/SPG_3/PCONTROL/CODICI/MULTIMODEL/Climatologie/MLD/Grid_GFDL/MLD_multimodel_mean.npy'

# Caricamento dei dati
MLD_multimodel_mean = np.load(path_mld_multimodel_mean)

# Caricamento delle coordinate
lat = np.load('/Users/marcobuccellato/Documents/Dottorato/2025_2026/SPG_3/PCONTROL/CODICI/MULTIMODEL/Coordinate/lat_GFDL_gr.npy')
lon = np.load('/Users/marcobuccellato/Documents/Dottorato/2025_2026/SPG_3/PCONTROL/CODICI/MULTIMODEL/Coordinate/lon_GFDL_gr.npy')

# Percorsi dei file .nc e implementazione variabili
# LOPS OBSERVATIONS
fn_LOPS = '/Users/marcobuccellato/Documents/Dottorato/2025_2026/SPG_3/PCONTROL/DATASETS/LOPS/MLD/mld_dr003_ref10m_v2023.nc'
ds_LOPS = nc.Dataset(fn_LOPS)

MLD_conv_multimodel_mean = np.load('/Users/marcobuccellato/Documents/Dottorato/2025_2026/SPG_3/PCONTROL/CODICI/MULTIMODEL/Climatologie/MLD/Grid_GFDL/MLD_conv_multimodel.npy')

# Estrazione variabili
MLD_LOPS = ds_LOPS['mld_dr003'][:, 90:, :]
lat_LOPS = ds_LOPS['lat'][90:]
lon_LOPS = ds_LOPS['lon'][:]

MLD_conv_LOPS = np.load('/Users/marcobuccellato/Documents/Dottorato/2025_2026/SPG_3/PCONTROL/CODICI/OBS_LOPS/MLD/Output/MLD_conv_LOPS.npy')


# ORAS5 REANALYSIS
fn_ORAS5 = '/Users/marcobuccellato/Documents/Dottorato/2025_2026/SPG_3/PCONTROL/DATASETS/ORAS5/MLD/ORAS5_mld_mar.nc'
ds_ORAS5 = nc.Dataset(fn_ORAS5)

MLD_conv_ORAS5 = np.load('/Users/marcobuccellato/Documents/Dottorato/2025_2026/SPG_3/PCONTROL/CODICI/REANALYSIS_ORAS5/MLD/Output/MLD_conv_ORAS5', allow_pickle=True)

# Estrazione variabili
MLD_ORAS5 = ds_ORAS5['somxl030'][:, :, :]
lat_ORAS5 = ds_ORAS5['nav_lat'][:, :]
lon_ORAS5 = ds_ORAS5['nav_lon'][:, :]


# Funzione per identificare la regione convettiva
def boolean_converter_a(array):
    return array > 1000

# Creazione della griglia 2D di latitudine e longitudine
lon_grid, lat_grid = np.meshgrid(lon, lat)

# Applicazione delle condizioni
lat_condition = (lat_grid > 50) & (lat_grid < 65)
lon_condition = (lon_grid > 295) & (lon_grid < 340)  # Convertito in gradi negativi per lon
Swdom = lat_condition & lon_condition

# === Plotting maps ===

models = [['GFDL', 'MRI', 'CNRM'], 
          ['MPI', 'CESM2', 'Had']]

model_name = [['GFDL-CM4', 'MRI-ESM2.0', 'CNRM-CM6-1-HR'], 
          ['MPI-ESM1.2', 'CESM2', 'HadGEM3-GC3.1-MM']]

labels = [['a)', 'b)', 'c)'], 
        ['d)', 'e)', 'f)']]

proj = ccrs.Mollweide(central_longitude=-30)
fig, ax = plt.subplots(3, 3, figsize=(12, 8), facecolor="w", subplot_kw=dict(projection=proj))

# Limiti geografici
lon_dx = 5
lon_sx = -70
lat_down = 45
lat_up = 90

# Livelli per il plot
levels = list(range(100, 1500, 50))  # Intervallo di profondità

# Dominio Swingedouw
lon_box = np.linspace(-65, -20, 100)
lat_bottom = np.full_like(lon_box, 50)
lat_top = np.full_like(lon_box, 65)
lon_left = np.full_like(np.linspace(50, 65, 100), -65)
lon_right = np.full_like(np.linspace(50, 65, 100), -20)
lat_side = np.linspace(50, 65, 100)

lon_rect = np.concatenate([lon_box, lon_right, lon_box[::-1], lon_left])
lat_rect = np.concatenate([lat_bottom, lat_side[::-1], lat_top[::-1], lat_side])


for i in range(2):
    for j in range(3):
        model = models[i][j]
        path_model = f'/Users/marcobuccellato/Documents/Dottorato/2025_2026/SPG_3/PCONTROL/CODICI/MULTIMODEL/Climatologie/MLD/Grid_GFDL/MLD_{model}_regridded_to_GFDL.npy'
        model_mean = np.load(path_model, allow_pickle=True)
        # globals()[f'MLD_{model}'] = model_mean
        ax[i][j].contourf(lon, lat, model_mean, levels=levels, extend='both', cmap='Blues', transform=ccrs.PlateCarree())
        ax[i][j].set_title(f'{model_name[i][j]}', fontsize=10)
        ax[i][j].contour(lon, lat, boolean_converter_a(model_mean)*Swdom, colors='k', linewidths=0.7, linestyles='dashed', transform=ccrs.PlateCarree())
        ax[i][j].text(0.02, 1.1, labels[i][j], transform=ax[i][j].transAxes, fontsize=10, fontweight='bold', va='top', ha='left')
        ax[i][j].set_extent((lon_sx, lon_dx, lat_down, lat_up))
        ax[i][j].coastlines('50m')
        ax[i][j].add_feature(cfeature.LAND, zorder=100, color='k', edgecolor='k')
        ax[i][j].plot(lon_rect, lat_rect, transform=ccrs.PlateCarree(), color='limegreen', linewidth=1, linestyle='--')

# Plot della MLD climatologica multimodel
cf1 = ax[2][0].contourf(lon, lat, MLD_multimodel_mean, levels=levels, extend='both', cmap='Blues', transform=ccrs.PlateCarree())
ax[2][0].set_title('Multimodel mean', fontsize=10)

# Plot della MLD climatologica osservativa
cf2 = ax[2][1].contourf(lon_LOPS, lat_LOPS, MLD_LOPS[2, :, :], levels=levels, extend='both', cmap='Blues', transform=ccrs.PlateCarree())
ax[2][1].set_title('Observations (LOPS)', fontsize=10)

# Plot della MLD climatologica rianalizzata
cf2 = ax[2][2].contourf(lon_ORAS5, lat_ORAS5, ma.mean(MLD_ORAS5, axis=0), levels=levels, extend='both', cmap='Blues', transform=ccrs.PlateCarree())
ax[2][2].set_title('Reanalysis (ORAS5)', fontsize=10)   

# Aggiungi label a) e b) ai subplot
ax[2][0].text(0, 1.1, 'g)', transform=ax[2][0].transAxes, fontsize=10, fontweight='bold', va='top', ha='left')
ax[2][1].text(0, 1.1, 'h)', transform=ax[2][1].transAxes, fontsize=10, fontweight='bold', va='top', ha='left')
ax[2][2].text(0, 1.1, 'i)', transform=ax[2][2].transAxes, fontsize=10, fontweight='bold', va='top', ha='left')

ax[2][0].contour(lon, lat, boolean_converter_a(MLD_multimodel_mean), colors='k', linewidths=0.7, linestyles='dashed', transform=ccrs.PlateCarree())
ax[2][1].contour(lon_LOPS, lat_LOPS, boolean_converter_a(MLD_LOPS[2, :, :]), colors='k', linewidths=0.7, linestyles='dashed', transform=ccrs.PlateCarree())
ax[2][2].contour(lon_ORAS5, lat_ORAS5, MLD_conv_ORAS5, colors='k', linewidths=0.7, linestyles='dashed', transform=ccrs.PlateCarree())


# Evidenziazione della regione convettiva
for a in range(3):
    ax[2][a].coastlines('50m')
    ax[2][a].plot(lon_rect, lat_rect, transform=ccrs.PlateCarree(),
            color='limegreen', linewidth=1, linestyle='--')
    ax[2][a].set_extent((lon_sx, lon_dx, lat_down, lat_up))
    ax[2][a].add_feature(cfeature.LAND, zorder=100, color='k', edgecolor='k')

# Riduci lo spazio tra i subplot e alza la posizione
#plt.subplots_adjust(left=0.07, right=0.93, top=0.88, bottom=0.22, wspace=0.04)

# Creazione della colorbar orizzontale sotto le figure
cbar_ax = fig.add_axes([0.17, 0.07, 0.6, 0.015])  # [left, bottom, width, height]
cbar = fig.colorbar(cf1, cax=cbar_ax, orientation='horizontal')
cbar.set_label('MLD (m)', fontsize=10, labelpad=5)

# Formattazione della colorbar
cbar.ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
cbar.ax.yaxis.offsetText.set_fontsize(10)

# Titolo generale
plt.suptitle(r'Comparison of mean MLD$_{March}$ for multimodel, observations and reanalysis datasets', y=0.95)

# Mostra il grafico
plt.show()

# Salvataggio della figura
fig.savefig('/Users/marcobuccellato/Documents/Dottorato/2025_2026/SPG_3/PCONTROL/CODICI/MULTIMODEL/Climatologie/MLD/Figure/MLD_clim_single_models_obs_reanalysis_12.1.png', dpi=300)