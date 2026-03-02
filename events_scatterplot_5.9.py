import numpy as np
import os
import matplotlib.pyplot as plt

# Directory output
output_dir = '/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Scatterplot/NEW/Output/'

# Lista modelli
models = ['CESM2', 'HadGEM3', 'MPI', 'GFDL', 'MRI', 'CNRM']
#models = ['MPI']

# Colori per ogni modello (puoi personalizzarli)
colors = {
    'CESM2': 'tab:blue',
    'HadGEM3': 'tab:orange',
    'MPI': 'tab:green',
    'GFDL': 'tab:red',
    'MRI': 'tab:purple',
    'CNRM': 'tab:brown'
}

# Crea il plot
plt.figure(figsize=(9,6))


# Loop per modello
for model in models:
    # Percorsi file
    nao_djfm_path = os.path.join('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Scatterplot/NEW/Output/NAO_DJFM', f'NAO_index_boxes_DJFM_{model}.npy')
    drho_path = os.path.join('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Scatterplot/NEW/Output/SSD_DJFM', f'Deltarho_DJFM_standardised_{model}_alpha_new.npy')

    # Percorso per gli indici di MLD
    mld_indexes_path = os.path.join('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/MLD_TS/Output', f'MLD_{model}_minima_indexes.npy')
    if model == 'MPI':
        # Eccezione per MPI, usa un percorso diverso
        mld_indexes_path = os.path.join('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/MLD_TS/Output', f'MLD_{model}_minima_indexes_500.npy')

    # Caricamento
    indexes = np.load(mld_indexes_path)  # (n_min,)
    nao_djfm = np.load(nao_djfm_path)[indexes]  # (n_min,)
    drho_djfm = np.load(drho_path)[indexes]  # (n_min,)

    # Caricamento dati
    nao_djfm_all = np.load(nao_djfm_path)  # tutti gli anni
    drho_djfm_all = np.load(drho_path)     # tutti gli anni

    # Scatter con colore specifico (inverti x e y)
    plt.scatter(drho_djfm, nao_djfm, label=model, alpha=0.7,
                edgecolors='k', s=40, c=colors[model])

    # Se il modello è MPI, aggiungi etichette con gli indici
    # if model == 'MPI':
    #     for idx, x, y in zip(indexes, drho_djfm, nao_djfm):
    #         plt.text(x, y, str(idx), fontsize=8, ha='right', va='bottom')
    
    plt.scatter(drho_djfm_all, nao_djfm_all,
                alpha=0.05, s=40, color=colors[model], marker='o')

    if model == 'GFDL':
        print(np.array((nao_djfm, drho_djfm)))

# # SUSPECT TIPPING     
# # Aggiungo allo scatterplot i punti di MPI associati alla 'Great Salinity Anomaly', eliminando la prima entrata:
# #indexes_MPI_tip = np.load('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MPI/MLD/Output/MLD_MPI_minima_indexes.npy')[1:]
# indexes_MPI_tip = np.linspace(270, 289, 20, dtype=int)  # Indici per i punti di MPI associati alla 'Great Salinity Anomaly'

# drho_djfm_tip = np.load(drho_path)[indexes_MPI_tip]  
# nao_djfm_tip = np.load(nao_djfm_path)[indexes_MPI_tip]  

# plt.scatter(drho_djfm, nao_djfm, alpha=0.7, marker='x',
#             s=40, c=colors['MPI'])



#             # Numerazione dei punti
# for idx, (x, y) in zip(indexes_MPI_tip, zip(drho_djfm_tip, nao_djfm_tip)):
#     # Offset personalizzato per i punti quasi sovrapposti
#     if idx == indexes_MPI_tip[1]:  # secondo punto
#         plt.text(x + 0.12, y + 0.12, str(idx), fontsize=9, ha='left', va='bottom')
#     elif idx == indexes_MPI_tip[4]:  # quinto punto
#         plt.text(x - 0.12, y - 0.12, str(idx), fontsize=9, ha='right', va='top')
#     else:
#         plt.text(x, y, str(idx), fontsize=9, ha='right', va='bottom')

# DETTAGLIA FIGURA
# Etichette e stile (inverti x e y)
plt.xlabel(r'Standardized surface density $\Delta \rho$')
plt.ylabel(r'NAO Index')
plt.title('Surface density anomalies (DJFM) vs. NAO index during shallow convection events')
plt.grid(True, alpha=0.3, linestyle='--')
plt.legend(title='Model')

# Colora il terzo quadrante (ora x<0, y<0, quindi inverti)
xlim = -7
ylim = -4
plt.axvspan(xlim, 0, ymin=0, ymax=0.5, facecolor='gray', alpha=0.15, zorder=0)
plt.axhspan(ylim, 0, xmin=0, xmax=0.5, facecolor='gray', alpha=0.15, zorder=0)
plt.tight_layout()
plt.legend(loc='upper right')
plt.xlim(xlim, 7)
plt.ylim(ylim, 4)
plt.axvline(0, color='k', linestyle='-', linewidth=0.8)
plt.axhline(0, color='k', linestyle='-', linewidth=0.8)

# Salvataggio
save_path = os.path.join(output_dir, 'scatterplot_Drho_NAO_13.10.png')
plt.savefig(save_path, dpi=300)
# Salvataggio della figura per stesura manoscritto
# LR
plt.savefig('/home/buccellato/work_big/SPG/PCONTROL/CODICI/_FIGURE_DEFINITIVE/LR/FIGURE_5_LR_13.10.png', dpi=150)
# HR
plt.savefig('/home/buccellato/work_big/SPG/PCONTROL/CODICI/_FIGURE_DEFINITIVE/HR/FIGURE_5_HR_13.10.png', dpi=600)

plt.close()

print(f"✅ Scatterplot salvato in: {save_path}")