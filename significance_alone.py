import numpy as np
import os
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# === Config ===
variables = ['SST', 'SSS', 'SHF', 'SLP', 'SAT']
models = ['CESM2', 'HadGEM3', 'GFDL', 'MRI', 'CNRM', 'MPI']
N = 2  # Almeno N modelli d'accordo

base_path = '/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Minima/March/Significance'
lon = np.load('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Coordinate/lon_GFDL_gr.npy')
lat = np.load('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Coordinate/lat_GFDL_gr.npy')

# === Plotting ===
fig, axes = plt.subplots(2, 3, figsize=(16, 8), subplot_kw={'projection': ccrs.PlateCarree()})
axes = axes.flatten()

for idx, var in enumerate(variables):
    masks = []
    for model in models:
        file_path = f"{base_path}/{var}/{var}_{model}_significance_regridded_to_GFDL.npy"
        if os.path.exists(file_path):
            mask = np.load(file_path)
            masks.append(mask)

    ax = axes[idx]
    ax.set_title(var)
    ax.coastlines()
    ax.set_global()
    ax.add_feature(cfeature.LAND, facecolor='lightgrey')

    if masks:
        stack = np.stack(masks)
        common_mask = np.sum(stack, axis=0) >= N
        if np.any(common_mask):
            ax.contourf(lon, lat, common_mask, levels=[0.5, 1], colors='crimson', transform=ccrs.PlateCarree())
        else:
            ax.text(0.5, 0.5, "No significant\npoints", transform=ax.transAxes,
                    ha='center', va='center', fontsize=10, color='gray')
    else:
        ax.text(0.5, 0.5, "No data", transform=ax.transAxes,
                ha='center', va='center', fontsize=10, color='gray')

# Rimuove eventuali subplot vuoti
for j in range(len(variables), len(axes)):
    axes[j].axis('off')

plt.suptitle(f"Zone con significatività comune (≥ {N} modelli)", fontsize=16)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.show()
# Salva il grafico
output_path = f"/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Minima/March/Significance_common_mask_{N}_models.png"
plt.savefig(output_path, bbox_inches='tight', dpi=300)