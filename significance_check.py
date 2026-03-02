import numpy as np
import os

# === Config ===
variables = ['SST', 'SSS', 'SHF', 'SLP', 'SAT']
models = ['CESM2', 'HadGEM3', 'GFDL', 'MRI', 'CNRM', 'MPI']  # Modelli da considerare
N = 3  # Soglia per considerare un punto "comune" tra almeno N modelli

base_path = '/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Minima/March/Significance'
any_true = {}

for var in variables:
    masks = []
    for model in models:
        file_path = f"{base_path}/{var}/{var}_{model}_significance_regridded_to_GFDL.npy"
        if os.path.exists(file_path):
            mask = np.load(file_path)
            masks.append(mask)
        else:
            print(f"⚠️ File mancante: {file_path}")

    if masks:
        stack = np.stack(masks)
        common_mask = np.sum(stack, axis=0) >= N
        has_significance = np.any(common_mask)
        any_true[var] = has_significance
        print(f"{var}: {'✅ qualche punto significativo comune' if has_significance else '❌ nessun punto significativo comune'}")
    else:
        print(f"{var}: ❌ nessuna maschera caricata")
        any_true[var] = False

# Riepilogo finale
print("\n------ Riepilogo -------")
print(any_true)
