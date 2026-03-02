import numpy as np
import os
import matplotlib.pyplot as plt

# Marco, 1.11. Si ristruttura la figura, si distribuiscono i grafici in 3 righe e 2 colonne.
# Poi si fissa l'asse x comune a tutti i subplot.


# Lista dei modelli
models = [['CESM2', 'HadGEM3'],
          ['CNRM', 'GFDL'],
          ['MRI', 'MPI']]

models_title = [['CESM2', 'HadGEM3-GC3.1-MM'],
          ['CNRM-CM6-1-HR', 'GFDL-CM4'],
          ['MRI-ESM2.0', 'MPI-ESM1.2']]

base_to_files = '/Users/marcobuccellato/Documents/Dottorato/2025_2026/SPG_3/PCONTROL/CODICI/MULTIMODEL/MLD_TS/Output/MLD_'

# PLOT #
n_rows, n_cols = 3, 2
fig, ax = plt.subplots(nrows=n_rows,ncols=n_cols, figsize=(16, 12))
half_window = 10

for i in range(n_rows):
    for j in range(n_cols):
        model_name = models[i][j]
        model_title = models_title[i][j]
        
        file_ts = os.path.join(base_to_files + model_name + '_TS.npy')
        file_indexes = os.path.join(base_to_files + model_name + '_minima_indexes.npy')
        file_threshold = os.path.join(base_to_files + model_name + '_minima_threshold.npy')
        
        MLD_TS = np.load(file_ts)
        indexes = np.load(file_indexes)
        threshold = np.load(file_threshold)
        
        t = np.linspace(0, len(MLD_TS) - 1, len(MLD_TS))
        MLD_TS_smooth_mobile = np.zeros(len(MLD_TS))

        for k in range(len(MLD_TS)):
            start = max(0, k - half_window)
            end = min(len(MLD_TS), k + half_window + 1)
            MLD_TS_smooth_mobile[k] = np.mean(MLD_TS[start:end])

        ax[i, j].plot(t, MLD_TS, 'r', linewidth=0.5, alpha=0.8, label='unfiltered')
        ax[i, j].plot(t, MLD_TS_smooth_mobile, 'brown', linewidth=1.5, label='high-filtered')
        # ax[i, j].set_ylabel('MLD (m)')
        # ax[i, j].set_xlabel('Model year')
        ax[i, j].set_title(model_title, fontsize=10)
        ax[i,j].grid(axis='both')
        ax[i, j].axhline(y=threshold, color='k', linestyle='dashed', alpha=0.3)
        ax[i, j].axhspan(0, threshold, color='lightblue', alpha=0.2)
        ax[i, j].scatter(indexes, MLD_TS[indexes])
        ax[i, j].set_xlim(0, 1000)
        ax[i, j].set_ylim(0, 3200)


indexes_500_MPI = np.load('/Users/marcobuccellato/Documents/Dottorato/2025_2026/SPG_3/PCONTROL/CODICI/MPI/MLD/Output/MLD_MPI_minima_indexes_500.npy')

ax[2,1].axhline(y=500, color='r', linestyle='dashed', alpha=0.3)
ax[2,1].scatter(indexes_500_MPI, MLD_TS[indexes_500_MPI], color='r', alpha=0.3)
# ax[1,2].axvspan(270, 290, color='coral', alpha=0.4)


fig.supxlabel('Model year', y=0.05, fontsize=12)
fig.supylabel('MLD (m)', x=0.03, fontsize=12)
plt.suptitle('Multimodel March $\pi$-control SPG mixed layer depth', y=0.97, fontsize=18)
plt.show()

fig.savefig('/Users/marcobuccellato/Documents/Dottorato/2025_2026/SPG_3/PCONTROL/CODICI/MULTIMODEL/MLD_TS/MLD_TS_multimodel_15.11.png', dpi=200)

# Salvataggio della figura per stesura manoscritto
# LR
fig.savefig('/Users/marcobuccellato/Documents/Dottorato/2025_2026/MANOSCRITTO_1/Jul25/FIGURE/_FIGURE_DEFINITIVE/LR/FIGURE_2_LR_15.11.png', dpi=150)
# HR
fig.savefig('/Users/marcobuccellato/Documents/Dottorato/2025_2026/MANOSCRITTO_1/Jul25/FIGURE/_FIGURE_DEFINITIVE/HR/FIGURE_2_HR_15.11.png', dpi=600)