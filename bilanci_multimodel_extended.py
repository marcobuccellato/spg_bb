import numpy as np
import os

# Marco, 19.6.25. Script per calcolare i bilanci multimodello estesi.

# Marco, 15.1. Caricamento delle deviazioni standard sigma_rho e sigma_F calcolate in sigma_rho_computation.py. 
# I file di prima erano probabilmente sbagliati; non si può capire ciò dato che work_big è stato cancellato ed è riapparso nel frattempo.

# Lista dei modelli
models = ['CESM2', 'HadGEM3', 'MPI', 'GFDL', 'MRI', 'CNRM']

# Directory base dei modelli
base_dir = '/home/buccellato/work_big/SPG/PCONTROL/CODICI/'


# Directory di output multimodello
output_dir = '/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Bilanci_extended/Output/Evoluzioni_temporali_multimodel'
os.makedirs(output_dir, exist_ok=True)

# Inizializzazione liste per accumulare i dati
Drho_list = []
Drho_T_list = []
Drho_S_list = []
DF_list = []
NAO_list = []

# Costanti
alpha = 0.00008 * np.ones(31)
beta = 0.00076 * np.ones(31)
rho_0 = 1028

for model in models:
    path = os.path.join(base_dir, 'MULTIMODEL/Bilanci_extended/Output/Evoluzioni_temporali')

    # Caricamento dati
    dT = np.load(os.path.join(path, f'SST/evoluzione_composite_dT_{model}_extended.npy'))
    dS = np.load(os.path.join(path, f'SSS/evoluzione_composite_dS_{model}_extended.npy'))
    DF = np.load(os.path.join(path, f'SHF/evoluzione_composite_DF_{model}_extended.npy'))
    NAO = np.load(os.path.join(path, f'NAO/evoluzione_composite_NAO_{model}_extended.npy'))

    # CARICAMENTO DEVIAZIONI STANDARD RHO E F
    # Carica il file con 13 valori
    sig_rho_old = np.load(f'/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Bilanci_extended/Output/Sigmas/SSD/sig_rho_monthly_{model}.npy')
    sig_DF_old = np.load(f'/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Bilanci_extended/Output/Sigmas/SHF/sig_F_monthly_{model}.npy')

    # Estendi ciclicamente fino a 31 mesi
    sig_rho = np.tile(sig_rho_old, (31 // len(sig_rho_old)) + 1)[:31]
    sig_DF = np.tile(sig_DF_old, (31 // len(sig_DF_old)) + 1)[:31]

    # Calcolo Drho, Drho_T e Drho_S
    Drho_T = -alpha * dT * rho_0 / sig_rho
    Drho_S = beta * dS * rho_0 / sig_rho
    Drho = Drho_T + Drho_S
    DF_norm = DF / sig_DF

    print(f"Model: {model} DT: {dT[18:25]}")
    #print(f"Model: {model} DF_norm: {DF_norm[21:25]}")


    # Accumulo
    Drho_list.append(Drho)
    DF_list.append(DF_norm)
    NAO_list.append(NAO)
    Drho_T_list.append(Drho_T)
    Drho_S_list.append(Drho_S)

# Conversione in array per calcolo statistico
Drho_array = np.array(Drho_list)
DF_array = np.array(DF_list)
NAO_array = np.array(NAO_list)
Drho_T_array = np.array(Drho_T_list)
Drho_S_array = np.array(Drho_S_list)

# Calcolo della media multimodello e dello spread (deviazione standard)
Drho_mean = np.mean(Drho_array, axis=0)
Drho_std = np.std(Drho_array, axis=0)

DF_mean = np.mean(DF_array, axis=0)
DF_std = np.std(DF_array, axis=0)

NAO_mean = np.mean(NAO_array, axis=0)
NAO_std = np.std(NAO_array, axis=0)

Drho_T_mean = np.mean(Drho_T_array, axis=0)
Drho_T_std = np.std(Drho_T_array, axis=0)

Drho_S_mean = np.mean(Drho_S_array, axis=0)
Drho_S_std = np.std(Drho_S_array, axis=0)

# print(DF_mean[21:24])
# print(DF_std[21:24])
# print(NAO_mean[21:24])
# print(NAO_std[21:24])
# print(Drho_mean[21:24])
# print(Drho_std[21:24])
# print(Drho_T_mean[21:24])
# print(Drho_T_std[21:24])
# print(Drho_S_mean[21:24])
# print(Drho_S_std[21:24])

# # Salvataggio su file .npy
# np.save(os.path.join(output_dir, 'Drho_mean_extended.npy'), Drho_mean)
# np.save(os.path.join(output_dir, 'Drho_std_extended.npy'), Drho_std)

# np.save(os.path.join(output_dir, 'DF_mean_extended.npy'), DF_mean)
# np.save(os.path.join(output_dir, 'DF_std_extended.npy'), DF_std)

# np.save(os.path.join(output_dir, 'NAO_mean_extended.npy'), NAO_mean)
# np.save(os.path.join(output_dir, 'NAO_std_extended.npy'), NAO_std)

# np.save(os.path.join(output_dir, 'Drho_T_mean_extended.npy'), Drho_T_mean)
# np.save(os.path.join(output_dir, 'Drho_T_std_extended.npy'), Drho_T_std)

# np.save(os.path.join(output_dir, 'Drho_S_mean_extended.npy'), Drho_S_mean)
# np.save(os.path.join(output_dir, 'Drho_S_std_extended.npy'), Drho_S_std)

# print("Salvataggio completato ✅")