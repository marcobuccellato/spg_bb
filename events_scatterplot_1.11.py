import numpy as np
import os
import matplotlib.pyplot as plt

# Marco, 1.11. Si stampa lo scatterplot a lag vari di NAO index vs Drho durante gli eventi di convezione superficiale
# Si opera sul locale, per cui si cambiano i percorsi dei file




# Directory output
output_dir = '/Users/marcobuccellato/Documents/Dottorato/2025_2026/SPG_3/PCONTROL/CODICI/MULTIMODEL/Scatterplot/NEW/Output/'

# Lista modelli
models = ['CESM2', 'HadGEM3', 'MPI', 'GFDL', 'MRI', 'CNRM']
models_title = ['CESM2', 'HadGEM3-GC3.1-MM', 'MPI-ESM1.2', 'GFDL-CM4', 'MRI-ESM2.0', 'CNRM-CM6-1-HR']
                
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
    nao_djfm_path = os.path.join('/Users/marcobuccellato/Documents/Dottorato/2025_2026/SPG_3/PCONTROL/CODICI/MULTIMODEL/Scatterplot/NEW/Output/NAO_DJFM', f'NAO_index_boxes_DJFM_{model}.npy')
    drho_path = os.path.join('/Users/marcobuccellato/Documents/Dottorato/2025_2026/SPG_3/PCONTROL/CODICI/MULTIMODEL/Scatterplot/NEW/Output/SSD_DJFM', f'Deltarho_DJFM_standardised_{model}_alpha_new.npy')

    # Percorso per gli indici di MLD
    mld_indexes_path = os.path.join('/Users/marcobuccellato/Documents/Dottorato/2025_2026/SPG_3/PCONTROL/CODICI/MULTIMODEL/MLD_TS/Output', f'MLD_{model}_minima_indexes.npy')
    if model == 'MPI':
        # Eccezione per MPI, usa un percorso diverso
        mld_indexes_path = os.path.join('/Users/marcobuccellato/Documents/Dottorato/2025_2026/SPG_3/PCONTROL/CODICI/MULTIMODEL/MLD_TS/Output', f'MLD_{model}_minima_indexes_500.npy')

    # Caricamento
    indexes = np.load(mld_indexes_path)  # (n_min,)
    indexes_minus_1 = indexes - 1        # array di valori indexes-1

    # NAO all'anno precedente (lag -1)
    nao_djfm_lag1 = np.load(nao_djfm_path)[indexes_minus_1]

    # Maschera per la condizione richiesta
    mask_lag1 = nao_djfm_lag1 < -0.5

    nao_djfm = np.load(nao_djfm_path)[indexes]  # (n_min,)
    drho_djfm = np.load(drho_path)[indexes]  # (n_min,)

    # Caricamento dati
    nao_djfm_all = np.load(nao_djfm_path)[:]   
    drho_djfm_all = np.load(drho_path)[:]    


    # Eventi standard
    plt.scatter(
        drho_djfm[~mask_lag1],
        nao_djfm[~mask_lag1],
        s=40,
        c=colors[model],
        label=models_title[models.index(model)],
        marker='o',
        edgecolors='k',
        alpha=0.8
    )

    # # Eventi preceduti da NAO < -0.5
    # plt.scatter(
    #     drho_djfm[mask_lag1],
    #     nao_djfm[mask_lag1],
    #     s=40,
    #     c=colors[model],
    #     marker='o',
    #     edgecolors='k',
    #     linewidths=1.8,
    #     alpha=1
    # )

    # Eventi con NAO_lag-1 < 0.5 (marker diverso)
    plt.scatter(
        drho_djfm[mask_lag1],
        nao_djfm[mask_lag1],
        alpha=0.9,
        edgecolors='k',
        s=40,
        c=colors[model],
        marker='v'
    )


    plt.scatter(drho_djfm_all, nao_djfm_all,
                alpha=0.05, s=40, color=colors[model], marker='o')



# DETTAGLIA FIGURA
# Etichette e stile (inverti x e y)
plt.xlabel(r'Standardized surface density $\Delta \rho$')
plt.ylabel(r'NAO Index')
plt.title(r'$\Delta \rho$ (DJFM) vs. NAO during shallow convection events')
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
save_path = os.path.join(output_dir, 'scatterplot_Drho_NAO_16.1.26_triangles.png')
plt.savefig(save_path, dpi=300)

plt.show()

# Salvataggio della figura per stesura manoscritto
# LR
#plt.savefig('/home/buccellato/work_big/SPG/PCONTROL/CODICI/_FIGURE_DEFINITIVE/LR/FIGURE_5_LR_13.10.png', dpi=150)
# HR
#plt.savefig('/home/buccellato/work_big/SPG/PCONTROL/CODICI/_FIGURE_DEFINITIVE/HR/FIGURE_5_HR_13.10.png', dpi=600)

plt.close()

print(f"✅ Scatterplot salvato in: {save_path}")