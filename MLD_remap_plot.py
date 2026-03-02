import numpy as np
import os
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt
import matplotlib.path as mpath
from matplotlib.path import Path


lat = np.load('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Coordinate/lat_GFDL_gr.npy')
lon = np.load('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Coordinate/lon_GFDL_gr.npy')

# Lista dei modelli
models = ['CESM2', 'Had', 'MPI', 'GFDL', 'MRI', 'CNRM']

MLD_list = []

for model in models:
    print(model)
    MLD_model = np.load(os.path.join('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Climatologie/MLD/Grid_GFDL/MLD_' + model +'_regridded_to_GFDL.npy'),
                        allow_pickle=True)
    MLD_list.append(MLD_model)

MLD_list = np.array(MLD_list)
MLD_mean = np.mean(MLD_list, axis=0)
np.save('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Climatologie/MLD/MLD_multimodel_mean.npy', MLD_mean)

# PLOT
# Proiezioni e figura:
#proj = ccrs.PlateCarree()  
proj = ccrs.LambertConformal(central_longitude=-30, central_latitude=58.0)

#proj = ccrs.Mollweide(central_longitude=-30)
fig, ax = plt.subplots(1,1, figsize=(8, 5), facecolor="w", 
    subplot_kw=dict(projection=proj))

# lon_dx = 180
# lon_sx = -180
# lat_down = -90
# lat_up = 90

lon_dx=10
lon_sx=-69
lat_down=40
lat_up=80

n = 30
aoi = mpath.Path(
    list(zip(np.linspace(lon_sx,lon_dx, n), np.full(n, lat_up))) + \
    list(zip(np.full(n, lon_dx), np.linspace(lat_up, lat_down, n))) + \
    list(zip(np.linspace(lon_dx, lon_sx, n), np.full(n, lat_down))) + \
    list(zip(np.full(n, lon_sx), np.linspace(lat_down, lat_up, n)))
)

# Livelli e regione convettiva:
levels  = list(range(250,1250, 20)) # Blues, turbo, ocean
cf = ax.contourf(lon, lat, MLD_mean, levels=levels, extend='both', cmap='Blues', transform=ccrs.PlateCarree())
#ax.contour(lon, lat, MLD_conv, colors='k', linewidths=1, linestyles='dashed',transform=ccrs.PlateCarree()) 

# Proprietà mappa:
# plt.clim(0,580)
ax.coastlines('50m')
#ax.set_boundary(aoi, transform=ccrs.PlateCarree())
ax.set_extent((lon_sx, lon_dx, lat_down, lat_up))
ax.add_feature(cfeature.LAND, zorder=100, color='k', edgecolor='k')
#ax.gridlines(False)
ax.set_position([0.1, 0.15, 0.8, 0.7]) # [left, bottom, width, height]

# Crea la colorbar
cbar_ax = fig.add_axes([0.9, 0.15, 0.02, 0.6])  # Regola le coordinate in modo che la colorbar sia a destra del grafico e regola l'altezza della colorbar
cbar = fig.colorbar(cf, cax=cbar_ax, orientation='vertical')

cbar.ax.set_title('$MLD$ (m)')

# Dominio Swingedouw
ax.plot([-60, -20, -20, -60, -60], [50, 50, 65, 65, 50], transform=ccrs.PlateCarree(), linestyle='-', color='g', linewidth=1.5)
#ax.plot([-60, -5, -5, -60, -60], [50, 50, 65, 65, 50], transform=ccrs.PlateCarree(), linestyle='-', color='g', linewidth=1.5)
#ax.plot([-68, -25, -25, -68, -68], [50, 50, 68, 68, 50], transform=ccrs.PlateCarree(), linestyle='-', color='g', linewidth=1.5)

# Titolo:
plt.suptitle('Multimodel mean March $\pi$-control mixed layer depth', y=0.93)
plt.show()
fig.savefig('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Climatologie/MLD//MLD_multimodel_mean_15.4_Mollweide.png', dpi=200)


