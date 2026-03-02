import numpy as np
import os

# Marco, 22.6. Si construiscono le composite per i bilanci di densità e flussi di calore.

# Lista dei modelli
#models = ['CESM2']
models = ['CESM2', 'HadGEM3', 'MPI', 'GFDL', 'MRI', 'CNRM']

# Directory base dei modelli
base_dir = '/home/buccellato/work_big/SPG/PCONTROL/CODICI/'

# Directory di output multimodello
output_dir = '/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Bilanci_extended/Output/Evoluzioni_temporali'
os.makedirs(output_dir, exist_ok=True)


months_index = list(range(-22, 9))  # Indici dei mesi da -22 a 8 (inclusi)


for model in models:
    print(f"\n🔁 Processing model: {model}")
    path = os.path.join(base_dir, 'MULTIMODEL/Bilanci_extended/Output')

    # Caricamento dati
    dT_LS_piControl = np.load(os.path.join(path, f'Serie temporali/SST/piControl_SST_anomalia_{model}.npy'))
    dS_LS_piControl = np.load(os.path.join(path, f'Serie temporali/SSS/piControl_SSS_anomalia_{model}.npy'))
    DF_LS_piControl = np.load(os.path.join(path, f'Serie temporali/SHF/piControl_SHF_anomalia_{model}.npy'))
    NAO_index_piControl = np.load(os.path.join(path, f'Serie temporali/NAO/NAO_index_boxes_{model}_18.6.npy'))
    
    # Creazione delle liste per le composite
    dT_composite = []
    dS_composite = []
    DF_composite = []
    NAO_composite = []

    if model == 'MPI':
        minima_indexes = np.load(os.path.join(base_dir, f'MULTIMODEL/MLD_TS/Output/MLD_{model}_minima_indexes_500.npy'))
    else:
        minima_indexes = np.load(os.path.join(base_dir, f'MULTIMODEL/MLD_TS/Output/MLD_{model}_minima_indexes.npy'))

    #print(minima_indexes.shape)

    # print(np.load('/home/buccellato/work_big/SPG/PCONTROL/CODICI/CESM2/MULTIVARIATE/Bilanci/Output/sst_monthly.npy'))
    # print(np.load('/home/buccellato/work_big/SPG/PCONTROL/CODICI/CESM2/MULTIVARIATE/Bilanci/Output/sss_monthly.npy'))
    # print(np.load('/home/buccellato/work_big/SPG/PCONTROL/CODICI/CESM2/MULTIVARIATE/Bilanci/Output/shf_monthly.npy'))


    for month in months_index: 
        # Calcolo la media per ogni mese rispetto agli indici minimi
        dT_month = np.mean(dT_LS_piControl[minima_indexes*12 + month])
        dS_month = np.mean(dS_LS_piControl[minima_indexes*12 + month])
        DF_month = np.mean(DF_LS_piControl[minima_indexes*12 + month])
        NAO_month = np.mean(NAO_index_piControl[minima_indexes*12 + month])
        # Aggiungo i risultati alle liste composite
        print(f'Mese {month}: dT={dT_month:.2f}, dS={dS_month:.2f}, DF={DF_month:.2f}, NAO={NAO_month:.2f}')
        dT_composite.append(dT_month)
        dS_composite.append(dS_month)
        DF_composite.append(DF_month)
        NAO_composite.append(NAO_month)

        # Salvataggio delle serie temporali composite
        # Creazione delle directory di output se non esistono
        for subdir in ['SST', 'SSS', 'SHF', 'NAO']:
            os.makedirs(os.path.join(output_dir, subdir), exist_ok=True)

        np.save(os.path.join(output_dir, f'SST/evoluzione_composite_dT_{model}_extended.npy'), np.array(dT_composite))
        np.save(os.path.join(output_dir, f'SSS/evoluzione_composite_dS_{model}_extended.npy'), np.array(dS_composite))
        np.save(os.path.join(output_dir, f'SHF/evoluzione_composite_DF_{model}_extended.npy'), np.array(DF_composite))
        np.save(os.path.join(output_dir, f'NAO/evoluzione_composite_NAO_{model}_extended.npy'), np.array(NAO_composite))

    print(np.array(dT_composite).shape())