import numpy as np
import os

# Marco, 15.1. In questo script si ricalcolano le deviazioni standard sigma_rho e sigma_F a partire dalle serie temporali di anomalie calolate in dT_dS_dF_TS_20.6.py.


models = ['CESM2', 'HadGEM3', 'GFDL', 'MRI', 'CNRM', 'MPI']
base_dir = '/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Bilanci_extended/Output/Serie temporali'
output_dir = '/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Bilanci_extended/Output/Sigmas'


# Parametri fisici
alpha, beta, rho_0 = 0.00008, 0.00076, 1028

for model in models:

    # Caricamento anomalie (1D arrays)
    T_anom = np.load(os.path.join(base_dir, f'SST/piControl_SST_anomalia_{model}.npy'))
    S_anom = np.load(os.path.join(base_dir, f'SSS/piControl_SSS_anomalia_{model}.npy'))
    F_anom = np.load(os.path.join(base_dir, f'SHF/piControl_SHF_anomalia_{model}.npy'))

    # Numero mesi
    n_months = 12

    # Output
    sig_F   = np.zeros(n_months)
    sig_rho = np.zeros(n_months)

    # Ordine: Marzo → Febbraio
    month_indices = [(2 + i) % 12 for i in range(n_months)]

    for i, m in enumerate(month_indices):

        # Selezione di tutti gli anni per quel mese
        Fm = F_anom[m::12]
        Tm = T_anom[m::12]
        Sm = S_anom[m::12]

        # Deviazione standard SHF
        sig_F[i] = np.std(Fm)

        # Anomalia di densità
        rho_anom = rho_0 * (-alpha * Tm + beta * Sm)

        # Deviazione standard densità
        sig_rho[i] = np.std(rho_anom)

        print(f"{i+1:02d} model={model} month_index={m}  σF={sig_F[i]:.3f}  σρ={sig_rho[i]:.3f}")

    # Salvataggio output
    os.makedirs(output_dir, exist_ok=True)
    np.save(os.path.join(output_dir, f'SHF/sig_F_monthly_{model}.npy'), sig_F)
    np.save(os.path.join(output_dir, f'SSD/sig_rho_monthly_{model}.npy'), sig_rho)