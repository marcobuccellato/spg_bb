import numpy as np
import netCDF4 as nc
import numpy.ma as ma
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import matplotlib.path as mpath
from matplotlib.ticker import ScalarFormatter

# Marco, 22.1. In questo file si uniscono le figure 1 e 2 del paper precedentemente sottomesso; a sinistra (fig1a) la MLD climatologica multimodel,
# a destra (fig1b) le serie temporali multimodel della MLD nella regione convettiva, modello per modello.

# Forse ha senso produrle separa

# === Configurazione ===

# Percorsi dei file FIGURE 1a
# MULTIMODEL MEAN
path_mld_multimodel_mean = '/Users/marcobuccellato/Documents/Dottorato/2025_2026/SPG_3/PCONTROL/CODICI/MULTIMODEL/Climatologie/MLD/Grid_GFDL/MLD_multimodel_mean.npy'

# Caricamento dei dati
MLD_multimodel_mean = np.load(path_mld_multimodel_mean)

# Caricamento delle coordinate
lat = np.load('/Users/marcobuccellato/Documents/Dottorato/2025_2026/SPG_3/PCONTROL/CODICI/MULTIMODEL/Coordinate/lat_GFDL_gr.npy')
lon = np.load('/Users/marcobuccellato/Documents/Dottorato/2025_2026/SPG_3/PCONTROL/CODICI/MULTIMODEL/Coordinate/lon_GFDL_gr.npy')


def boolean_converter_a(array, threshold=1000):
    """
    Identifica convezione profonda (MLD > threshold)
    """
    return array > threshold


# Percorsi dei file FIGURE 1b



# === Plotting maps ===

proj = ccrs.Mollweide(central_longitude=-30)

fig, ax = plt.subplots(
    1, 1,
    figsize=(8, 5),
    facecolor="w",
    subplot_kw=dict(projection=proj)
)

# Limiti geografici
lon_dx = 5
lon_sx = -70
lat_down = 45
lat_up = 90

# Livelli MLD
levels = np.arange(0, 1501, 50)

# MLD multimodel mean
cf1 = ax.contourf(
    lon, lat, MLD_multimodel_mean,
    levels=levels,
    extend='max',
    cmap='Blues',
    transform=ccrs.PlateCarree()
)

# Contorno convezione profonda
ax.contour(
    lon, lat,
    boolean_converter_a(MLD_multimodel_mean),
    levels=[0.5],
    colors='k',
    linewidths=0.8,
    linestyles='dashed',
    transform=ccrs.PlateCarree()
)

# Etichetta pannello
ax.text(
    -0.05, 1.02, 'a)',
    transform=ax.transAxes,
    fontsize=10,
    fontweight='bold',
    va='bottom',
    ha='left'
)

# Dominio Swingedouw
lon_box = np.linspace(-65, -20, 100)
lat_bottom = np.full_like(lon_box, 50)
lat_top = np.full_like(lon_box, 65)
lat_side = np.linspace(50, 65, 100)

lon_rect = np.concatenate([lon_box, np.full_like(lat_side, -20),
                            lon_box[::-1], np.full_like(lat_side, -65)])
lat_rect = np.concatenate([lat_bottom, lat_side,
                            lat_top[::-1], lat_side[::-1]])

ax.plot(
    lon_rect, lat_rect,
    transform=ccrs.PlateCarree(),
    color='limegreen',
    linewidth=1,
    linestyle='--'
)

# Cartografia
ax.coastlines('50m', linewidth=0.8)
ax.add_feature(cfeature.LAND, zorder=100, color='k', edgecolor='k')

ax.set_extent(
    (lon_sx, lon_dx, lat_down, lat_up),
    crs=ccrs.PlateCarree()
)

# Layout
plt.subplots_adjust(left=0.07, right=0.93, top=0.88, bottom=0.22)

# Colorbar
cbar_ax = fig.add_axes([0.25, 0.10, 0.5, 0.02])
cbar = fig.colorbar(cf1, cax=cbar_ax, orientation='horizontal')
cbar.set_label('MLD (m)', fontsize=9)
cbar.ax.tick_params(labelsize=8)

# Titolo generale
plt.suptitle(r'Mean multimodel MLD$_{March}$', y=0.95)

plt.show()

# Salvataggio della figura
fig.savefig('/Users/marcobuccellato/Documents/Dottorato/2025_2026/SPG_3/PCONTROL/CODICI/MULTIMODEL/Climatologie/MLD/Figure/MLD_clim_multimodel_22.1.png', dpi=300)