import numpy as np
import os

# Marco, 13.10. Si introduce anche qui un diverso valore di alpha, seguendo Roquet et al., 2022.

# Costanti per la densità
#alpha = 0.00017
alpha = 0.00008  # valore di Roquet et al., 2022, T=4-5°C, S=34.5-35 psu
beta = 0.00076
rho_0 = 1028

# Lista dei modelli
models = ['CESM2', 'HadGEM3', 'MPI', 'GFDL', 'MRI', 'CNRM']

# Directory base e output
base_dir = '/home/buccellato/work_big/SPG/PCONTROL/CODICI/'
input_path = os.path.join(base_dir, 'MULTIMODEL/Bilanci_extended/Output')
output_path = os.path.join(base_dir, 'MULTIMODEL/Scatterplot/NEW/Output/SSD_DJFM')
os.makedirs(output_path, exist_ok=True)

for model in models:
    print(f"\n🔁 Processing model: {model}")

    # Caricamento anomalie mensili ΔT e ΔS
    dT = np.load(os.path.join(input_path, f'Serie temporali/SST/piControl_SST_anomalia_{model}.npy'))
    dS = np.load(os.path.join(input_path, f'Serie temporali/SSS/piControl_SSS_anomalia_{model}.npy'))

    assert dT.shape == dS.shape, "ΔT e ΔS devono avere la stessa lunghezza"

    # Calcolo di Δρ
    delta_rho = rho_0 * (-alpha * dT + beta * dS)

    # Ricostruzione serie DJFM annuale
    n_months = len(delta_rho)
    n_years = n_months // 12
    years = list(range(n_years))

    annual_djfm_rho = []

    for y in years:
        months = []

        # Dicembre dell'anno precedente (se esiste)
        if y > 0:
            months.append(delta_rho[y * 12 - 1])  # Dicembre

        # Gennaio, Febbraio, Marzo
        jan = y * 12
        if jan + 2 < n_months:
            months.extend([delta_rho[jan], delta_rho[jan + 1], delta_rho[jan + 2]])
        else:
            months.extend([m for i, m in enumerate(delta_rho[jan:jan + 3]) if jan + i < n_months])

        if months:
            annual_djfm_rho.append(np.mean(months))

    annual_djfm_rho = np.array(annual_djfm_rho)

    # Standardizzazione (z-score)
    mean_rho = np.mean(annual_djfm_rho)
    std_rho = np.std(annual_djfm_rho)
    standardized_rho = (annual_djfm_rho - mean_rho) / std_rho
    # Percorso file con indici di convezione interrotta
    mld_indexes_path = os.path.join(
        '/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/MLD_TS/Output',
        f'MLD_{model}_minima_indexes.npy'
    )

    # Eccezione per MPI
    if model == 'MPI':
        mld_indexes_path = os.path.join(
            '/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/MLD_TS/Output',
            f'MLD_{model}_minima_indexes_500.npy'
        )

    # Carica indici e stampa media se esistono
    if os.path.exists(mld_indexes_path):
        indexes = np.load(mld_indexes_path).tolist()

        # Filtro per evitare out-of-range
        valid_indexes = [i for i in indexes if i < len(standardized_rho)]

        if valid_indexes:
            mean_value = np.mean(standardized_rho[valid_indexes])
            print(f"📉 Mean DJFM Δρ index for MLD minima years in {model}: {mean_value:.3f}")
        else:
            print(f"⚠️ Nessun indice valido per {model} (fuori range).")
    else:
        print(f"❌ MLD minima indexes file not found for model {model}. Skipping mean calculation.")

    # Salvataggio
    out_file = os.path.join(output_path, f'Deltarho_DJFM_standardised_{model}_alpha_new.npy')
    np.save(out_file, standardized_rho)
    print(f"✅ Salvato: {out_file} ({len(standardized_rho)} anni)")

