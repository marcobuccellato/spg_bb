import numpy as np 
import xarray as xr 
import matplotlib.pyplot as plt 
import matplotlib.patheffects as path_effects 

# Marco, 8.10. Inserisco l'informazione su NAO nel grafico dell'Hovmoller. 
# # Opzione 1: coloro di blu gli anni con NAO- estremo (definiti come NAO_DJFM < -1) 
# # Opzione 2: disegno un marker accanto agli anni con NAO - 

# ========================== 
# FILES 
# ========================== 
fn_SSS = "/home/buccellato/work_big/SPG/PCONTROL/DATASETS/MPI/SSS/piMPI_SSS_Datasets/gr/sos_MPI_piControl_gr.nc" 

ilat_ord = np.load("/home/buccellato/work_big/SPG/PCONTROL/CODICI/MPI/MULTIVARIATE/Tipping_event/Parcel_tracing/Output/ilat_ord.npy") 
ilon_ord = np.load("/home/buccellato/work_big/SPG/PCONTROL/CODICI/MPI/MULTIVARIATE/Tipping_event/Parcel_tracing/Output/ilon_ord.npy") 

dist = np.load("/home/buccellato/work_big/SPG/PCONTROL/CODICI/MPI/MULTIVARIATE/Tipping_event/Parcel_tracing/Output/dist_cum.npy") 
npoints = len(ilat_ord) 

indexes = np.load("/home/buccellato/work_big/SPG/PCONTROL/CODICI/MPI/MLD/Output/MLD_MPI_minima_indexes.npy") 
indexes = indexes[1:] 
indexes_500_tip = np.load("/home/buccellato/work_big/SPG/PCONTROL/CODICI/MPI/MLD/Output/MLD_MPI_minima_indexes_500_tip.npy") 
indexes_extreme_NAO_minus = [270, 271, 272, 279, 280, 281] 

for i, d in enumerate(dist): 
    print(f"{i}: {d}") 
    
# ========================== 
# SALINITÀ 
# ========================== 
 
print("Carico dataset...") 

ds = xr.open_dataset(fn_SSS, chunks={"time": 12}) 
sss = ds["sos"].isel(lat=slice(90, None)) # stesso taglio del filmato 
# climatologia mensile 
sss_clim = sss.groupby("time.month").mean("time") 
sss_anom = sss.groupby("time.month") - sss_clim 
# finestra temporale anni 270–290 (270*12 = 3240, 290*12 = 3480 → +12 per arrivare a dicembre 290 = 3492) 
sss_anom_window = sss_anom.isel(time=slice(3240, 3492)) 
ntime = sss_anom_window.sizes["time"] 

# ========================== 
# SELEZIONE STREAMLINE 
# ========================== 
# vettore tempo × punti 
hov = sss_anom_window.isel(lat=(("points",), ilat_ord), lon=(("points",), ilon_ord)) 
hov = hov.values # converto in numpy array [time, npoints] 
print("Hovmöller shape:", hov.shape) 

# ========================== 
# COSTRUZIONE ASSE TEMPO (anni.mesi)
# ========================== 

year0 = 270 
months = np.arange(ntime) 
years = year0 + months // 12
mon = (months % 12) + 1
time_axis = years + (mon - 1) / 12.0  # anno.mese decimale

# ==========================
# PLOT
# ==========================
times = sss_anom_window["time"].values
fig, ax = plt.subplots(figsize=(9, 6))

cf = ax.contourf(
    dist, time_axis, hov,
    levels=np.linspace(-1, 1, 41),
    cmap="PuOr_r", extend="both"
)

y_ticks = np.arange(270, 291, 1)
ax.set_yticks(y_ticks)

# Colore etichette
yticklabels = ax.get_yticklabels()
for i in range(y_ticks.shape[0]):
    # if y_ticks[i] in indexes_extreme_NAO_minus:
    #     yticklabels[i].set_path_effects([
    #         path_effects.Stroke(linewidth=1, foreground='blue'),
    #         path_effects.Normal()
    #     ])
    if y_ticks[i] in indexes_500_tip:
        yticklabels[i].set_color('blue')

# Simbolo accanto alle etichette
for label, yval in zip(yticklabels, y_ticks):
    if yval in indexes_extreme_NAO_minus:
        # Ottieni posizione testo
        x_pos = label.get_position()[0]
        y_pos = label.get_position()[1]
        # Disegna un piccolo marker blu accanto all’etichetta
        ax.plot(
            [x_pos - 0.08], [y_pos],
            marker='v', color='blue', markersize=4,
            transform=ax.get_yaxis_transform(), clip_on=False
        )

# Linee orizzontali e verticali
ax.axvline(x=dist[11], color='white', linestyle='--', linewidth=1)
for idx in indexes_500_tip:
    ax.axhline(y=idx, color='red', linestyle='--', linewidth=1.2)

# Testi sopra il grafico
ax.text(
    dist[4], time_axis[-1] + 0.2, 'Irminger Sea',
    color='black', fontsize=8, va='bottom', ha='left'
)
ax.text(
    dist[18], time_axis[-1] + 0.2, 'Labrador Sea',
    color='black', fontsize=8, va='bottom', ha='left'
)

# Barra dei colori
cbar = plt.colorbar(cf, ax=ax, orientation='vertical', shrink=0.8, pad=0.07)
cbar.ax.set_title(r'$\Delta S$ (psu)', fontsize=10)

# Etichette assi
ax.set_xlabel("Distance along the track (km)", labelpad=10)
ax.set_ylabel("Time (years)", labelpad=14)

# # Salvataggio e visualizzazione
# plt.savefig(
#     "/home/buccellato/work_big/SPG/PCONTROL/CODICI/MPI/MULTIVARIATE/"
#     "Tipping_event/Parcel_tracing/Figure/hovmoller_SSS_GC_8_10_NOTITLE.png",
#     dpi=600
# )
#plt.show()

# Salvataggio figura a bassa e alta risoluzione
# LR
fig.savefig('/home/buccellato/work_big/SPG/PCONTROL/CODICI/_FIGURE_DEFINITIVE/LR/FIGURE_6_c_LR_16.10_bis.png', dpi=150)
# HR
fig.savefig('/home/buccellato/work_big/SPG/PCONTROL/CODICI/_FIGURE_DEFINITIVE/HR/FIGURE_6_c_HR_16.10_bis.png', dpi=600)
