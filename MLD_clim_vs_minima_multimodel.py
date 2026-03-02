import numpy as np
import numpy.ma as ma
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import matplotlib.path as mpath
from matplotlib.ticker import ScalarFormatter

# === Configurazione ===
# Percorsi dei file .npy
path_mld_mean = '/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Climatologie/MLD/Grid_GFDL/MLD_multimodel_mean.npy'
path_mld_minima = '/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Minima/March/MLD/MLD_multimodel_mean.npy'

# Caricamento dei dati
MLD_mean = np.load(path_mld_mean)
MLD_minima = np.load(path_mld_minima)

# Caricamento delle coordinate
lat = np.load('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Coordinate/lat_GFDL_gr.npy')
lon = np.load('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Coordinate/lon_GFDL_gr.npy')


print(lon)


# Funzione per identificare la regione convettiva
def boolean_converter_a(array):
    return array > 1000

# Creazione della griglia 2D di latitudine e longitudine
lon_grid, lat_grid = np.meshgrid(lon, lat)

# Applicazione delle condizioni
lat_condition = (lat_grid > 50) & (lat_grid < 65)
lon_condition = (lon_grid > 295) & (lon_grid < 340)  # Convertito in gradi negativi per lon
Swdom = lat_condition & lon_condition

# Identificazione della regione convettiva
MLD_conv = boolean_converter_a(MLD_mean) * Swdom
output_path = '/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Climatologie/MLD/Grid_GFDL/MLD_conv_multimodel.npy'
np.save(output_path, MLD_conv)

MLD_mean = ma.masked_invalid(MLD_mean)

print("MLD_mean min:", ma.min(MLD_mean))
print("MLD_mean max:", ma.max(MLD_mean))

# Proiezione e configurazione della figura
proj = ccrs.LambertConformal(central_longitude=-30, central_latitude=58.0)
fig, ax = plt.subplots(1, 2, figsize=(10, 6), facecolor="w", subplot_kw=dict(projection=proj))

# Limiti geografici
lon_dx = 10
lon_sx = -69
lat_down = 40
lat_up = 80

# Area of interest (AOI)
n = 30
aoi = mpath.Path(
    list(zip(np.linspace(lon_sx, lon_dx, n), np.full(n, lat_up))) +
    list(zip(np.full(n, lon_dx), np.linspace(lat_up, lat_down, n))) +
    list(zip(np.linspace(lon_dx, lon_sx, n), np.full(n, lat_down))) +
    list(zip(np.full(n, lon_sx), np.linspace(lat_down, lat_up, n)))
)

# Livelli per il plot
levels = list(range(250, 1250, 50))  # Intervallo di profondità

# Plot della MLD climatologica
cf1 = ax[0].contourf(lon, lat, MLD_mean, levels=levels, extend='both', cmap='Blues', transform=ccrs.PlateCarree())
#ax[0].set_title('Multimodel mean', fontsize=10)

# Plot della MLD associata ai minimi
cf2 = ax[1].contourf(lon, lat, MLD_minima, levels=levels, extend='both', cmap='Blues', transform=ccrs.PlateCarree())
#ax[1].set_title('Multimodel minima', fontsize=10)

# Aggiungi label a) e b) ai subplot
ax[0].text(0.02, 0.97, 'a)', transform=ax[0].transAxes, fontsize=10, fontweight='bold', va='top', ha='left')
ax[1].text(0.02, 0.97, 'b)', transform=ax[1].transAxes, fontsize=10, fontweight='bold', va='top', ha='left')

# Evidenziazione della regione convettiva
for a in ax:
    a.contour(lon, lat, MLD_conv, colors='k', linewidths=1, linestyles='dashed', transform=ccrs.PlateCarree())
    a.coastlines('50m')
    a.set_boundary(aoi, transform=ccrs.PlateCarree())
    a.set_extent((lon_sx, lon_dx, lat_down, lat_up))
    a.add_feature(cfeature.LAND, zorder=100, color='k', edgecolor='k')

# Riduci lo spazio tra i subplot e alza la posizione
plt.subplots_adjust(left=0.07, right=0.93, top=0.88, bottom=0.22, wspace=0.04)

# Creazione della colorbar orizzontale sotto le figure
cbar_ax = fig.add_axes([0.17, 0.1, 0.65, 0.03])  # [left, bottom, width, height]
cbar = fig.colorbar(cf1, cax=cbar_ax, orientation='horizontal')
cbar.set_label('MLD (m)', fontsize=10, labelpad=5)

# Formattazione della colorbar
cbar.ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
cbar.ax.yaxis.offsetText.set_fontsize(10)

# Titolo generale
plt.suptitle(r'Multimodel mean MLD$_{March}$ and composite fields associated to shallow convection states', y=0.93)

# Mostra il grafico
plt.show()

# Salvataggio della figura
fig.savefig('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Climatologie/MLD/MLD_multimodel_composite_with_convective_region_7.6_large.png', dpi=300)