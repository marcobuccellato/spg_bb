import numpy as np
import os
import matplotlib.pyplot as plt

# Marco, 13.4. In questo file si raccolgono le serie temporali dei diversi modelli e si stampano
# in un unico plot. 
# Si organizzano le variabili in funzione del plot, che strutturo con tre colonne e due righe.
# Si ricordi che:
# - alla serie temporale CESM2 importata qui sono stati rimossi i primi 200 anni per potenziale influenza dello spinup
# - gli indici associati ai minimi di MLD nella simulazione MPI usano il criterio di soglia arbitraria a 500 m
# - la selezione eventi sulla serie temporale di CNRM è stata svolta rimuovendo una modulante di bassa frequenza  

# Lista dei modelli
models = [['CESM2', 'HadGEM3', 'CNRM'],
          ['GFDL', 'MRI', 'MPI']]

base_to_files = '/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/MLD_TS/Output/MLD_'

# PLOT #
n_rows, n_cols = 2, 3
fig, ax = plt.subplots(nrows=n_rows,ncols=n_cols, figsize=(12, 8))
half_window = 10

for i in range(n_rows):
    for j in range(n_cols):
        model_name = models[i][j]
        
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
        ax[i, j].set_title(model_name, fontsize=10)
        ax[i,j].grid(axis='both')
        ax[i, j].axhline(y=threshold, color='k', linestyle='dashed', alpha=0.3)
        ax[i, j].axhspan(0, threshold, color='lightblue', alpha=0.2)
        ax[i, j].scatter(indexes, MLD_TS[indexes])
        ax[i, j].set_xlim(0, len(MLD_TS))
        ax[i, j].set_ylim(0, 3200)


# indexes_500_MPI = np.load('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MPI/MLD/Output/MLD_MPI_minima_indexes_500.npy')

# ax[1,2].axhline(y=500, color='r', linestyle='dashed', alpha=0.3)
# ax[1,2].scatter(indexes_500_MPI, MLD_TS[indexes_500_MPI], color='r', alpha=0.3)
# ax[1,2].axvspan(270, 290, color='coral', alpha=0.4)


fig.supxlabel('Model year', y=0.05, fontsize=12)
fig.supylabel('MLD (m)', x=0.03, fontsize=12)
plt.suptitle('Multimodel March $\pi$-control SPG mixed layer depth', y=0.97, fontsize=18)
plt.show()

fig.savefig('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/MLD_TS/MLD_TS_multimodel', dpi=200)

# Salvataggio della figura per stesura manoscritto
# LR
#fig.savefig('/home/buccellato/work_big/SPG/PCONTROL/CODICI/_FIGURE_DEFINITIVE/LR/FIGURE_2_LR_15.10.png', dpi=150)
# HR
#fig.savefig('/home/buccellato/work_big/SPG/PCONTROL/CODICI/_FIGURE_DEFINITIVE/HR/FIGURE_2_HR_15.10.png', dpi=600)