import numpy as np
import os

# Marco, 16.1. Alla fine questo codice non si è usato; non ce n'è stato bisogno visto
# il segnale molto coerente tra i modelli nel flusso di calore superficiale normalizzato (a 
# seguito di revisioni).

# Lista dei modelli
models = ['CESM2', 'HadGEM3', 'MPI', 'GFDL', 'MRI', 'CNRM']

# Directory base dei modelli
base_dir = '/home/buccellato/work_big/SPG/PCONTROL/CODICI/'


# Directory di output multimodello
output_dir = '/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Bilanci_extended/Output/Evoluzioni_temporali_multimodel'
os.makedirs(output_dir, exist_ok=True)

for model in models:
    path = os.path.join(base_dir, 'MULTIMODEL/Bilanci_extended/Output/Evoluzioni_temporali')

    # CARICAMENTO DEVIAZIONI STANDARD RHO E F
    # Carica il file con 13 valori
    sig_rho_old = np.load(os.path.join(base_dir, model, 'MULTIVARIATE/Bilanci/Output/sig_rho_monthly.npy'))
    sig_DF_old = np.load(os.path.join(base_dir, model, 'MULTIVARIATE/Bilanci/Output/sig_F_monthly.npy'))

    # Rimuovi l'ultimo valore (duplicato di marzo)
    sig_rho_old = sig_rho_old[:-1]  # ora ha 12 mesi da marzo a febbraio
    sig_DF_old = sig_DF_old[:-1]  # ora ha 12 mesi da marzo a febbraio

    print(f"Model: {model} sig_DF_old: {sig_DF_old}")
