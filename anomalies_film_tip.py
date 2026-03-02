import xarray as xr
import numpy as np
import xarray as xr
import numpy as np
import matplotlib
matplotlib.use("Agg")  # backend headless, nessun display richiesto
import shutil
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.path as mpath
import matplotlib.colors as mcolors

# Marco, 23.9.25. Si produce un filmato con le anomalie mensili di SSS, SST e SIC.

# === FILES ===
fn_SSS = "/home/buccellato/work_big/SPG/PCONTROL/DATASETS/MPI/SSS/piMPI_SSS_Datasets/gr/sos_MPI_piControl_gr.nc"
fn_SST = "/home/buccellato/work_big/SPG/PCONTROL/DATASETS/MPI/SST/piMPI_SST_Datasets/gr/tos_MPI_piControl_gr.nc"
fn_SIC = "/home/buccellato/work_big/SPG/PCONTROL/DATASETS/MPI/SIC/piMPI_SIC_Datasets/gn/siconca_MPI_piControl_gn_a.nc"

print("Loading datasets...")
# === APERTURA CON CHUNKS ===
ds_SSS = xr.open_dataset(fn_SSS, chunks={"time": 12})
ds_SST = xr.open_dataset(fn_SST, chunks={"time": 12})
ds_SIC = xr.open_dataset(fn_SIC, chunks={"time": 12})
print("Datasets loaded.")

# === SELEZIONE LAT >= 90 ===
lat_SSS = ds_SSS["lat"]
lat_SST = ds_SST["lat"]
lat_SIC = ds_SIC["lat"]

print("lat_SSS shape:", lat_SSS.shape)

print("lat_SSS range:", lat_SSS.min().item(), "to", lat_SSS.max().item())
print("lat_SST range:", lat_SST.min().item(), "to", lat_SST.max().item())
print("lat_SIC range:", lat_SIC.min().item(), "to", lat_SIC.max().item())

# === TAGLIO LATITUDINE A INDICE >= 90 ===
sss = ds_SSS["sos"].isel(lat=slice(90, None))
sst = ds_SST["tos"].isel(lat=slice(90, None))
sic = ds_SIC["siconca"].isel(lat=slice(90, None))

print("sss shape after lat selection:", sss.shape)
print("sst shape after lat selection:", sst.shape)
print("sic shape after lat selection:", sic.shape)

# === CLIMATOLOGIA MENSILE ===
sss_clim = sss.groupby("time.month").mean("time")
sst_clim = sst.groupby("time.month").mean("time")
sic_clim = sic.groupby("time.month").mean("time")

print("sss_clim shape:", sss_clim.shape)
print("sst_clim shape:", sst_clim.shape)
print("sic_clim shape:", sic_clim.shape)

# === ANOMALIE ===
sss_anom = sss.groupby("time.month") - sss_clim
sst_anom = sst.groupby("time.month") - sst_clim
sic_anom = sic.groupby("time.month") - sic_clim

print("sss_anom shape:", sss_anom.shape)
print("sst_anom shape:", sst_anom.shape)
print("sic_anom shape:", sic_anom.shape)

# === FINESTRA [270, 290] ===
sss_anom_window = sss_anom.isel(time=slice(3240, 3492))
sst_anom_window = sst_anom.isel(time=slice(3240, 3492))
sic_anom_window = sic_anom.isel(time=slice(3240, 3492))

print("sss_anom_window shape:", sss_anom_window.shape)
print("sst_anom_window shape:", sst_anom_window.shape)
print("sic_anom_window shape:", sic_anom_window.shape)

# # === CALCOLO MEDIA SULLA FINESTRA ===
# sss_anom_mean = sss_anom_window.mean("time")
# sst_anom_mean = sst_anom_window.mean("time")
# sic_anom_mean = sic_anom_window.mean("time")

# print("SSS anomalies mean shape:", sss_anom_mean.shape)
# print("SST anomalies mean shape:", sst_anom_mean.shape)
# print("SIC anomalies mean shape:", sic_anom_mean.shape)


# === PROIEZIONE E DOMINIO ===
proj = ccrs.LambertConformal(central_longitude=-30, central_latitude=58.0)

lon_dx = 10
lon_sx = -69
lat_down = 30
lat_up = 80

n = 30
aoi = mpath.Path(
    list(zip(np.linspace(lon_sx, lon_dx, n), np.full(n, lat_up))) +
    list(zip(np.full(n, lon_dx), np.linspace(lat_up, lat_down, n))) +
    list(zip(np.linspace(lon_dx, lon_sx, n), np.full(n, lat_down))) +
    list(zip(np.full(n, lon_sx), np.linspace(lat_down, lat_up, n)))
)

# === COLORMAPS SPECIFICHE ===
cmap_sss = "PuOr_r"       # Anomalia salinità
levels_sss = np.linspace(-0.8, 0.8, 15)

cmap_sst = "coolwarm"     # Anomalia temperatura superficiale
levels_sst = np.linspace(-3, 3, 13)

colors = ["darkred", "red", "lightcoral", "white", "white", "white", "deepskyblue", "blue", "darkblue"]

cmap_sic = mcolors.ListedColormap(colors)      # Copertura da ghiaccio marino
levels_sic = np.linspace(-20, 20, 9)

# === PREPARAZIONE FIGURA ===
fig, axes = plt.subplots(
    1, 3, figsize=(15, 5), facecolor="w",
    subplot_kw=dict(projection=proj)
)

variables = {
    "SSS Anomaly (psu)": {"data": sss_anom_window, "levels": levels_sss, "cmap": cmap_sss},
    "SST Anomaly (°C)": {"data": sst_anom_window, "levels": levels_sst, "cmap": cmap_sst},
    "SIC (%)": {"data": sic_anom_window * 100, "levels": levels_sic, "cmap": cmap_sic},  # convert to %
}

times = sss_anom_window["time"].values

# === FUNZIONE DI DISEGN0 FRAME ===
def update(frame):
    for ax, (title, cfg) in zip(axes, variables.items()):
        ax.clear()
        ax.set_extent((lon_sx, lon_dx, lat_down, lat_up))
        ax.set_boundary(aoi, transform=ccrs.PlateCarree())
        ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
        ax.add_feature(cfeature.LAND, color="lightgray")

        data = cfg["data"].isel(time=frame)
        cf = ax.contourf(
            data["lon"], data["lat"], data,
            levels=cfg["levels"], cmap=cfg["cmap"], extend="both",
            transform=ccrs.PlateCarree()
        )

        # # === COLORBAR SOTTO OGNI PANNELLO ===
        # cbar = plt.colorbar(
        #     cf, ax=ax, orientation="horizontal", fraction=0.046, pad=0.07
        # )
        # cbar.set_label(title, fontsize=8)
        # cbar.ax.tick_params(labelsize=7)

        ax.set_title(title, fontsize=10)

    # === TIME LABEL (year + month) ===
    year0 = 270
    year = year0 + frame // 12
    month = (frame % 12) + 1
    fig.suptitle(
        f"Monthly anomalies – Year {year}, Month {month}",
        y=0.92, fontsize=14
    )

# === ANIMAZIONE ===
ani = animation.FuncAnimation(fig, update, frames=len(times), interval=500, blit=False)

# === SALVATAGGIO ROBUSTO ===
if shutil.which("ffmpeg"):
    print(">> ffmpeg trovato: salvo come MP4")
    ani.save("/home/buccellato/work_big/SPG/PCONTROL/CODICI/MPI/MULTIVARIATE/Tipping_event/sss_sst_sic_anomalies.mp4", writer="ffmpeg", dpi=120)
    print("File salvato: sss_sst_sic_anomalies.mp4")
else:
    print(">> ffmpeg NON trovato: salvo come GIF con Pillow")
    ani.save("/home/buccellato/work_big/SPG/PCONTROL/CODICI/MPI/MULTIVARIATE/Tipping_event/sss_sst_sic_anomalies.gif", writer="pillow", dpi=100)
    print("File salvato: sss_sst_sic_anomalies.gif")