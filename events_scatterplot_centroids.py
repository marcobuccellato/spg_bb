import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

# Directory output
output_dir = '/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Scatterplot/NEW/Output/'

# Lista modelli
#models = ['CESM2', 'HadGEM3', 'MPI', 'GFDL', 'MRI', 'CNRM']
models = ['MPI']

# Colori per ogni modello
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

for model in models:
    # Percorsi file
    nao_djfm_path = os.path.join('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Scatterplot/NEW/Output/NAO_DJFM', f'NAO_index_boxes_DJFM_{model}.npy')
    drho_path = os.path.join('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Scatterplot/NEW/Output/SSD_DJFM', f'Deltarho_DJFM_standardised_{model}.npy')

    # Percorso per gli indici di MLD
    mld_indexes_path = os.path.join('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/MLD_TS/Output', f'MLD_{model}_minima_indexes.npy')
    if model == 'MPI':
        # Eccezione per MPI, usa un percorso diverso
        mld_indexes_path = os.path.join('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/MLD_TS/Output', f'MLD_{model}_minima_indexes_500.npy')

    # Caricamento
    indexes = np.load(mld_indexes_path)  # (n_min,)
    nao_djfm = np.load(nao_djfm_path)[indexes]  # (n_min,)
    drho_djfm = np.load(drho_path)[indexes]  # (n_min,)

    # Centroide
    x_mean = drho_djfm.mean()
    y_mean = nao_djfm.mean()

    # Deviazioni standard (spread)
    x_std = drho_djfm.std()
    y_std = nao_djfm.std()

    # Scatter solo del centroide
    plt.scatter(x_mean, y_mean, label=model, color=colors[model], edgecolors='k', s=80, zorder=3)

    # Aggiungi ellisse (1 sigma)
    ellipse = Ellipse((x_mean, y_mean), width=2*x_std, height=2*y_std,
                      facecolor=colors[model], alpha=0.2, edgecolor='none', zorder=2)
    plt.gca().add_patch(ellipse)


indexes_MPI_tip = np.load('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MPI/MLD/Output/MLD_MPI_minima_indexes.npy')[1:]
# indexes_MPI_tip = np.linspace(270, 289, 20, dtype=int) 
drho_djfm_tip = np.load(drho_path)[indexes_MPI_tip]  
nao_djfm_tip = np.load(nao_djfm_path)[indexes_MPI_tip]  

x_mean_tip = drho_djfm_tip.mean()
y_mean_tip = nao_djfm_tip.mean()

# Deviazioni standard (spread) per i punti di MPI
x_std_tip = drho_djfm_tip.std()
y_std_tip = nao_djfm_tip.std()

plt.scatter(x_mean_tip, y_mean_tip, color=colors['MPI'], edgecolors='k', s=80, zorder=3, marker='x')

# Aggiungi ellisse (1 sigma)
ellipse = Ellipse((x_mean_tip, y_mean_tip), width=2*x_std_tip, height=2*y_std_tip,
                  facecolor=colors[model], alpha=0.2, edgecolor='none', zorder=2)
plt.gca().add_patch(ellipse)



# Etichette e stile
plt.xlabel(r'Standardized surface density $\Delta \rho$')
plt.ylabel(r'NAO Index')
plt.title('Surface density anomalies (DJFM) vs. NAO index during shallow convection events')
plt.grid(True, alpha=0.3, linestyle='--')
plt.legend(title='Model', loc='upper right')

xlim = -7
ylim = -4

# Assi e guide
plt.axvspan(xlim, 0, ymin=0, ymax=0.5, facecolor='gray', alpha=0.15, zorder=0)
plt.axhspan(ylim, 0, xmin=0, xmax=0.5, facecolor='gray', alpha=0.15, zorder=0)
plt.axvline(0, color='k', linestyle='-', linewidth=0.8)
plt.axhline(0, color='k', linestyle='-', linewidth=0.8)
plt.xlim(xlim, 7)
plt.ylim(ylim, 4)
plt.tight_layout()

# Salvataggio
save_path = os.path.join(output_dir, 'scatterplot_Drho_NAO_30.7_centroids.png')
plt.savefig(save_path, dpi=300)
plt.close()

print(f"✅ Scatterplot con centroidi salvato in: {save_path}")
