import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Supponiamo di avere già:
# SST_TS, SSS_TS, SIC_TS (array della stessa lunghezza)
SST_TS = np.load('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MPI/MULTIVARIATE/Tipping_event/Serie_temporali_multivariate/Output/SST_TS_MPI.npy')
SSS_TS = np.load('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MPI/MULTIVARIATE/Tipping_event/Serie_temporali_multivariate/Output/SSS_TS_MPI.npy')
SIC_TS = np.load('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MPI/MULTIVARIATE/Tipping_event/Serie_temporali_multivariate/Output/SIC_TS_MPI.npy')

# Indici degli eventi di shutdown
indexes = np.load("/home/buccellato/work_big/SPG/PCONTROL/CODICI/MPI/MLD/Output/MLD_MPI_minima_indexes.npy")
indexes_500 = np.load("/home/buccellato/work_big/SPG/PCONTROL/CODICI/MPI/MLD/Output/MLD_MPI_minima_indexes_500.npy")

t = np.arange(len(SST_TS))  # tempo del modello (per colorare)

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# ---- Scatter generale (colore = tempo) ----
p = ax.scatter(
    SST_TS, SSS_TS, SIC_TS,
    color='gray', s=15, alpha=0.8,
    label='system state (all years)'
)

# ---- Evidenzia eventi speciali ----
ax.scatter(
    SST_TS[indexes], SSS_TS[indexes], SIC_TS[indexes],
    color='blue', s=60, edgecolor='k', label='shutdown events'
)

# ax.scatter(
#     SST_TS[indexes_500], SSS_TS[indexes_500], SIC_TS[indexes_500],
#     color='red', s=60, edgecolor='k', label='shutdown 500 events'
# )

# # ---- Finestra 270–290 ----
# window = np.arange(271, 291)
# ax.scatter(
#     SST_TS[window], SSS_TS[window], SIC_TS[window],
#     color='coral', s=40, label='270–290 window'
# )

# Disegna il piano SST=0 trasparente
ss_min, ss_max = 33.4, 35
sic_min, sic_max = 0, 80
ss_grid, sic_grid = np.meshgrid(
    np.linspace(ss_min, ss_max, 10),
    np.linspace(sic_min, sic_max, 10)
)
sst_plane = np.zeros_like(ss_grid)
ax.plot_surface(
    sst_plane, ss_grid, sic_grid,
    color='blue', alpha=0.1, linewidth=0, antialiased=False
)

# ---- Etichette & legenda ----
ax.set_xlabel("SST (°C)")
ax.set_ylabel("SSS (psu)")
ax.set_zlabel("SIC (%)")

ax.set_xlim(-2, 5)
ax.set_ylim(33.4, 35)
ax.set_zlim(0, 80)

ax.set_title("Phase-space scatter (SST–SSS–SIC) of the SPG pi-control")

# cbar = fig.colorbar(p, ax=ax, pad=0.1)
# cbar.set_label("Model year (index)")

ax.legend()
plt.tight_layout()
plt.show()

plt.savefig("/home/buccellato/work_big/SPG/PCONTROL/CODICI/MPI/MULTIVARIATE/Tipping_event/Serie_temporali_multivariate/Figure/scatterplot_3d.png", dpi=300)
