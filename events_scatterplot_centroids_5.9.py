import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

# Funzione per ellisse basata sulla covarianza
def confidence_ellipse(x, y, ax, n_std=1.0, **kwargs):
    cov = np.cov(x, y)
    vals, vecs = np.linalg.eigh(cov)
    order = vals.argsort()[::-1]
    vals, vecs = vals[order], vecs[:, order]

    theta = np.degrees(np.arctan2(*vecs[:,0][::-1]))
    width, height = 2 * n_std * np.sqrt(vals)

    ellipse = Ellipse((np.mean(x), np.mean(y)), width, height,
                      angle=theta, **kwargs)
    return ax.add_patch(ellipse)

# Directory output (versione locale)
output_dir = '/Users/marcobuccellato/Documents/Dottorato/2024_2025/SPG_2/PCONTROL/CODICI/MULTIMODEL/Scatterplot/NEW/Output/'

# Lista modelli
models = ['CESM2', 'HadGEM3', 'MPI', 'GFDL', 'MRI', 'CNRM']

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
    # Percorsi file locali
    nao_djfm_path = os.path.join(output_dir, 'NAO_DJFM', f'NAO_index_boxes_DJFM_{model}.npy')
    drho_path = os.path.join(output_dir, 'SSD_DJFM', f'Deltarho_DJFM_standardised_{model}.npy')

    mld_indexes_path = os.path.join(
        '/Users/marcobuccellato/Documents/Dottorato/2024_2025/SPG_2/PCONTROL/CODICI/MULTIMODEL/MLD_TS/Output',
        f'MLD_{model}_minima_indexes.npy'
    )
    if model == 'MPI':
        mld_indexes_path = os.path.join(
            '/Users/marcobuccellato/Documents/Dottorato/2024_2025/SPG_2/PCONTROL/CODICI/MULTIMODEL/MLD_TS/Output',
            f'MLD_{model}_minima_indexes_500.npy'
        )

    # Caricamento dati
    indexes = np.load(mld_indexes_path)
    nao_djfm = np.load(nao_djfm_path)[indexes]
    drho_djfm = np.load(drho_path)[indexes]

    # Scatter del centroide
    x_mean, y_mean = drho_djfm.mean(), nao_djfm.mean()
    plt.scatter(x_mean, y_mean, label=model, color=colors[model], edgecolors='k', s=80, zorder=3)

    # Confidence ellipse (1 sigma)
    confidence_ellipse(drho_djfm, nao_djfm, plt.gca(), n_std=1,
                       facecolor=colors[model], alpha=0.2, edgecolor='none', zorder=2)

# # Caso MPI tip
# indexes_MPI_tip = np.load(
#     '/Users/marcobuccellato/Documents/Dottorato/2024_2025/SPG_2/PCONTROL/CODICI/MPI/MLD/Output/MLD_MPI_minima_indexes.npy'
# )[1:]

# drho_djfm_tip = np.load(drho_path)[indexes_MPI_tip]
# nao_djfm_tip = np.load(nao_djfm_path)[indexes_MPI_tip]

# x_mean_tip, y_mean_tip = drho_djfm_tip.mean(), nao_djfm_tip.mean()
# plt.scatter(x_mean_tip, y_mean_tip, color=colors['MPI'], edgecolors='k', s=80, zorder=3, marker='x')

# confidence_ellipse(drho_djfm_tip, nao_djfm_tip, plt.gca(), n_std=1,
#                    facecolor=colors['MPI'], alpha=0.2, edgecolor='none', zorder=2)

# Etichette e stile
plt.xlabel(r'Standardized surface density $\Delta \rho$')
plt.ylabel(r'NAO Index')
plt.title('Surface density anomalies (DJFM) vs. NAO index during shallow convection events')
plt.grid(True, alpha=0.3, linestyle='--')
plt.legend(title='Model', loc='upper right')

xlim, ylim = -7, -4
plt.axvspan(xlim, 0, ymin=0, ymax=0.5, facecolor='gray', alpha=0.15, zorder=0)
plt.axhspan(ylim, 0, xmin=0, xmax=0.5, facecolor='gray', alpha=0.15, zorder=0)
plt.axvline(0, color='k', linestyle='-', linewidth=0.8)
plt.axhline(0, color='k', linestyle='-', linewidth=0.8)
plt.xlim(xlim, 7)
plt.ylim(ylim, 4)
plt.tight_layout()

# Salvataggio
save_path = os.path.join(output_dir, 'scatterplot_Drho_NAO_5.9_centroids.png')
plt.savefig(save_path, dpi=300)
plt.close()

print(f"✅ Scatterplot con centroidi + confidence ellipse salvato in: {save_path}")