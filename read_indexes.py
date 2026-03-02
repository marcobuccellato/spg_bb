import numpy as np

# Marco, 30.7.25. Si scrive un codicino scemo per capire quali sono effettivamente gli indici MPI associati al collasso
# della convezione indotto da great salinity anomaly.

indexes_MPI = np.load('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MPI/MLD/Output/MLD_MPI_minima_indexes.npy')
indexes_MPI_500 = np.load('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MPI/MLD/Output/MLD_MPI_minima_indexes_500.npy')

print(np.linspace(270, 289, 20, dtype=int))
print(indexes_MPI_500)

# Marco, 15 ottobre. Si usa il codice per dare un'occhiata al file NAO_MPI

nao = np.load('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Scatterplot/NEW/Output/NAO_DJFM/NAO_index_boxes_DJFM_MPI.npy')

print(nao[265:292])