import numpy as np
import netCDF4 as nc
from pyproj import Geod
import matplotlib as mpl
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.patheffects

# =======================
# DATI
# =======================
# tuoi punti (indici già costruiti a mano)
pts_pochi = (
    np.array([59, 60, 61, 62, 63, 64, 65, 66, 67, 68,
              69, 69, 69, 70, 70, 70, 71, 71, 71, 72, 
              72, 72, 73, 73, 73, 74, 75, 76, 76, 77, 
              78, 79]),
    np.array([329, 328, 328, 328, 327, 325, 323, 322, 321, 320,
              320, 335, 338, 319, 332, 340, 319, 331, 340, 320, 
              329, 341, 322, 326, 342, 345, 348, 351, 354, 357, 
              359, 362])
)

# === Dataset ===
fn = '/home/buccellato/work_big/SPG/PCONTROL/DATASETS/MPI/BSF/piMPI_BSF_Datasets/gr/msftbarot_MPI_piControl_gr.nc'
ds = nc.Dataset(fn)

lat = ds['lat'][90:]
lon = ds['lon'][:]

# Maschera regione
lon2d, lat2d = np.meshgrid(lon, lat)

lat_seq = lat2d[pts_pochi]
lon_seq = lon2d[pts_pochi]
points = np.column_stack([lon_seq, lat_seq])

# =======================
# ORDINAMENTO
# =======================
geod = Geod(ellps="WGS84")

# punto iniziale ~ stretto di Danimarca
start_target = np.array([340, 65])
start_idx = np.argmin(np.sqrt(((points - start_target)**2).sum(axis=1)))

ordered = [start_idx]
unused = set(range(len(points)))
unused.remove(start_idx)

while unused:
    last = ordered[-1]
    dists = []
    for i in unused:
        _, _, dist_m = geod.inv(points[last,0], points[last,1],
                                points[i,0], points[i,1])
        dists.append((dist_m, i))
    _, next_idx = min(dists, key=lambda x: x[0])
    ordered.append(next_idx)
    unused.remove(next_idx)


print(ordered)

# sequenza ordinata
lon_ord = points[ordered,0]
lat_ord = points[ordered,1]

# =======================
# DISTANZE
# =======================
distanze_km = []
for i in range(len(lon_ord)-1):
    _, _, dist_m = geod.inv(lon_ord[i], lat_ord[i],
                            lon_ord[i+1], lat_ord[i+1])
    distanze_km.append(dist_m/1000)

dist_cum = np.cumsum([0] + distanze_km)

# # stampa tabella
# for i in range(len(lon_ord)):
#     print(f"{i:02d}: lon={lon_ord[i]:.2f}, lat={lat_ord[i]:.2f}, dist_cum={dist_cum[i]:.1f} km")

# print(f"\nDistanza totale lungo la streamline: {dist_cum[-1]:.1f} km")

# =======================
# PLOT
# =======================
proj = ccrs.LambertConformal(central_longitude=-30, central_latitude=58.0)
fig, ax = plt.subplots(1, 1, figsize=(8, 5), subplot_kw=dict(projection=proj))

# coastline + terra
ax.coastlines('50m')
ax.add_feature(cfeature.LAND, color='lightgray')
ax.add_feature(cfeature.OCEAN.with_scale('50m'), facecolor='lightblue')
ax.add_feature(cfeature.LAKES.with_scale('50m'), facecolor='lightblue')
# ax.add_feature(cfeature.RIVERS.with_scale('50m'), edgecolor='blue', alpha=0.5)

# scatter con distanza cumulativa
sc = ax.scatter(lon_ord, lat_ord, c=dist_cum, cmap='viridis',
                s=30, transform=ccrs.PlateCarree(), zorder=5)

# linea di collegamento
ax.plot(lon_ord, lat_ord, c='k', lw=0.8, transform=ccrs.PlateCarree())

# regione convettiva MPI
MLD_conv = np.load('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MPI/MLD/Output/MLD_conv_MPI_gn_a.npy')[90:, :-1]

# Crea una maschera booleana per la zona convettiva
conv_mask = (MLD_conv > 0.5).astype(float)

# Colora la zona convettiva con hatching (zigrinatura)
# Purtroppo, in Matplotlib non è possibile modificare direttamente la trasparenza (alpha) degli hatches: l'argomento alpha si applica solo al colore di sfondo, non alle linee degli hatches.
# Un workaround è usare hatches più sottili (densità maggiore) o cambiare il colore delle linee degli hatches (solo con contourf non è supportato direttamente).
# Se vuoi un effetto più "leggero", puoi provare a usare hatches meno fitti, ad esempio '//' invece di '////', oppure cambiare il colore di sfondo (facecolor) per renderlo più trasparente.
# ax.contourf(
#     lon, lat, conv_mask,
#     levels=[0.5, 1.1],
#     colors='none',
# #    hatches=['//'],  # meno fitto
#     alpha=0,  # lo sfondo resta trasparente
#     transform=ccrs.PlateCarree(),
#     zorder=2
# )

# Opzionale: bordo grigio per la zona convettiva
ax.contour(lon, lat, MLD_conv, levels=[0.5], colors='darkblue', linewidths=0.5, linestyles='--', transform=ccrs.PlateCarree(), zorder=3)

# estensione area
ax.set_extent((295, 340, 50, 70))

# colorbar con etichetta in km
cbar = plt.colorbar(sc, ax=ax, label="Distance (km)", pad=0.02, aspect=30)
cbar.ax.tick_params(labelsize=8)
cbar.set_label("Distance (km)", fontsize=9)

# =======================
# AGGIUNTA LABEL SULLA LINEA
# =======================
milestones = [1000, 2000, 3000, 4000]  # km
for m in milestones:
    # trova indice più vicino a questa distanza
    idx = np.argmin(np.abs(dist_cum - m))
    # Piccolo offset verso destra (in longitudine)
    offset_deg_lon = 0.6  # gradi di longitudine (~50-60 km)
    offset_deg_lat = 0.1  # gradi di latitudine (~10-15 km)
    ax.text(lon_ord[idx] + offset_deg_lon, lat_ord[idx]-offset_deg_lat, f"{m} km",
            transform=ccrs.PlateCarree(),
            fontsize=8, color="k", weight="book",
            ha="left", va="bottom",
            path_effects=[plt.matplotlib.patheffects.withStroke(linewidth=1.5, foreground="white")])

#plt.title("Gridpoints along the 3 Sv barotropic streamline in the SPG region", fontsize=10, pad=12)
#fig.savefig('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MPI/MULTIVARIATE/Tipping_event/Parcel_tracing/streamline_GC_distances_tris_NOTITLE.png', dpi=600)

# Salvataggio figura a bassa e alta risoluzione
# LR
fig.savefig('/home/buccellato/work_big/SPG/PCONTROL/CODICI/_FIGURE DEFINITIVE/LR/FIGURE_6_b_LR', dpi=150)
# HR
fig.savefig('/home/buccellato/work_big/SPG/PCONTROL/CODICI/_FIGURE DEFINITIVE/HR/FIGURE_6_b_HR', dpi=600)


# # =======================
# # SALVATAGGIO IN .NPY
# # =======================

# outdir = "/home/buccellato/work_big/SPG/PCONTROL/CODICI/MPI/MULTIVARIATE/Tipping_event/Parcel_tracing/Output"

# # --- Ricostruzione indici ordinati ---
# ilat_seq = pts_pochi[0]
# ilon_seq = pts_pochi[1]
# indici = np.column_stack([ilat_seq, ilon_seq])

# # usa la stessa lista "ordered" che abbiamo calcolato
# ilat_ord = ilat_seq[ordered]
# ilon_ord = ilon_seq[ordered]

# np.save(f"{outdir}/ilat_ord.npy", ilat_ord)
# np.save(f"{outdir}/ilon_ord.npy", ilon_ord)
# np.save(f"{outdir}/dist_cum.npy", np.array(dist_cum))

# print(ilat_ord)
# print(ilon_ord)
