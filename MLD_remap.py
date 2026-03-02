import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy.ma as ma

# === Load Data === #
lat_GFDL = np.load('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Coordinate/lat_GFDL_gr.npy')
lon_GFDL = np.load('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Coordinate/lon_GFDL_gr.npy')

lat_model = np.load('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Coordinate/lat_Had_gr.npy')
lon_model = np.load('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Coordinate/lon_Had_gr.npy')
MLD_model = np.load('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Climatologie/MLD/Grid_models/MLD_Had_March.npy', allow_pickle=True)

# === Flatten input for interpolation === #
lon_model_grid, lat_model_grid = np.meshgrid(lon_model, lat_model)
lon_GFDL_grid, lat_GFDL_grid = np.meshgrid(lon_GFDL, lat_GFDL)

# Rimuove i punti mascherati prima di interpolare
valid_mask = ~ma.getmaskarray(MLD_model)
valid_points = np.array([lon_model_grid[valid_mask], lat_model_grid[valid_mask]]).T
valid_values = MLD_model[valid_mask]

# === Interpolazione sulla griglia GFDL === #
MLD_interp = griddata(
    valid_points,
    valid_values,
    (lon_GFDL_grid, lat_GFDL_grid),
    method='nearest'
)

# Maschera i NaN
MLD_interp = ma.masked_invalid(MLD_interp)

MLD_interp.dump('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Climatologie/MLD/Grid_GFDL/MLD_Had_regridded_to_GFDL.npy')

# === Plot === #
fig, axs = plt.subplots(1, 2, figsize=(12, 5), subplot_kw={'projection': ccrs.PlateCarree()})

lon_dx=10
lon_sx=-69
lat_down=40
lat_up=80
extent = [lon_sx, lon_dx, lat_down, lat_up]

# Plot originale
cs1 = axs[0].pcolormesh(lon_model_grid, lat_model_grid, MLD_model, cmap='Blues')
axs[0].set_title('MLD originale (Had)')
axs[0].set_extent(extent, crs=ccrs.PlateCarree())
axs[0].coastlines()
axs[0].add_feature(cfeature.BORDERS)
fig.colorbar(cs1, ax=axs[0], orientation='vertical', shrink=0.7)

# Plot interpolato
cs2 = axs[1].pcolormesh(lon_GFDL_grid, lat_GFDL_grid, MLD_interp, cmap='Blues')
axs[1].set_title('MLD interpolato (su griglia GFDL)')
axs[1].set_extent(extent, crs=ccrs.PlateCarree())
axs[1].coastlines()
axs[1].add_feature(cfeature.BORDERS)
fig.colorbar(cs2, ax=axs[1], orientation='vertical', shrink=0.7)

plt.tight_layout()
plt.savefig('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Climatologie/MLD/MLD_Had_to_GFDL_interp_map.png', dpi=300)