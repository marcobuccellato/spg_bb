import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline
from matplotlib.ticker import FixedLocator, FuncFormatter
from matplotlib.patches import Rectangle
from matplotlib.legend_handler import HandlerBase

# === Directory dati ===
data_dir = '/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Bilanci_extended/Output/Evoluzioni_temporali_multimodel'

# === Caricamento dati estesi ===
Drho_mean = np.load(f'{data_dir}/Drho_mean_extended.npy')
Drho_std = np.load(f'{data_dir}/Drho_std_extended.npy')

DF_mean = np.load(f'{data_dir}/DF_mean_extended.npy')
DF_std = np.load(f'{data_dir}/DF_std_extended.npy')

NAO_mean = np.load(f'{data_dir}/NAO_mean_extended.npy')
NAO_std = np.load(f'{data_dir}/NAO_std_extended.npy')

Drho_T_mean = np.load(f'{data_dir}/Drho_T_mean_extended.npy')
Drho_T_std = np.load(f'{data_dir}/Drho_T_std_extended.npy')

Drho_S_mean = np.load(f'{data_dir}/Drho_S_mean_extended.npy')
Drho_S_std = np.load(f'{data_dir}/Drho_S_std_extended.npy')

print(DF_mean[21:25]+DF_std[21:25])
print(NAO_mean[21:25])


# === Etichette mesi per 31 mesi ===
months_labels = [
    "Mar$_{-2}$", "Apr", "May", "Jun", "Jul", "Aug", 
    "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar$_{-1}$",
    "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"
]
x = np.arange(len(months_labels))  # 0...30


# === Etichette temporali relative ===
x = np.arange(31)  # 0...30
event_index = 24   # Marzo evento
relative_labels = [f"{i - event_index:+d}" for i in x]


# Scatter valori di Marzo
x_Mar = np.array([0, 12 , 24])
MLD_Mar_anomalies_standardized = np.array([-0.32, -0.89, -2.64])

# === Funzione di smoothing ===
def smooth_data(x, y, smooth_factor=0):
    spline = UnivariateSpline(x, y, s=smooth_factor)
    x_smooth = np.linspace(x.min(), x.max(), 300)
    y_smooth = spline(x_smooth)
    return x_smooth, y_smooth

# === Funzioni di scala asimmetrica ===
power = 5/6
fwd = lambda y: np.sign(y) * (abs(y) ** power)
inv = lambda y: np.sign(y) * (abs(y) ** (1/power))


class SplitLegendHandle:
    def __init__(self, color_left='darkred', color_right='blue'):
        self.color_left = color_left
        self.color_right = color_right

class SplitLegendHandler(HandlerBase):
    def create_artists(self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans):
        # Crea due rettangoli affiancati
        r1 = Rectangle([xdescent, ydescent], width/2, height,
                       facecolor=orig_handle.color_left, edgecolor='k', lw=0.5, alpha=0.4, transform=trans)
        r2 = Rectangle([xdescent + width/2, ydescent], width/2, height,
                       facecolor=orig_handle.color_right, edgecolor='k', lw=0.5, alpha=0.4, transform=trans)
        return [r1, r2]


def plot_nao_df(output_path):
    x_smooth, F_smooth = smooth_data(x, DF_mean)
    _, F_std_smooth = smooth_data(x, DF_std)

    fig, ax1 = plt.subplots(figsize=(10, 6))
    colors = ['blue' if val < 0 else 'darkred' for val in NAO_mean]

    # Barre trasformate
    nao_transformed = fwd(NAO_mean)
    ax1.bar(
        x, nao_transformed,
        color=colors, alpha=0.4, label=r'$NAO$', zorder=0
    )

    # Errori trasformati
    nao_err_upper = fwd(NAO_mean + NAO_std)
    nao_err_lower = fwd(NAO_mean - NAO_std)
    nao_err = [nao_transformed - nao_err_lower, nao_err_upper - nao_transformed]

    ax1.errorbar(
        x, nao_transformed, yerr=nao_err,
        fmt='none', ecolor='k', capsize=3, elinewidth=1, alpha=0.9, zorder=1
    )

    line_handle = ax1.plot(x_smooth, fwd(F_smooth), linestyle='dotted', color='k', linewidth=2, label=r'$\Delta F$', zorder=1) [0]
    ax1.fill_between(x_smooth, fwd(F_smooth - F_std_smooth), fwd(F_smooth + F_std_smooth), color='black', alpha=0.1)
    split_handle = SplitLegendHandle()
    #line_handle = ax1.plot(x_smooth, F_smooth, linestyle='dotted', color='k', linewidth=2, label=r'$\Delta F$')[0]

    # Etichette asse x
    ax1.set_xticks(x)
    ax1.set_xticklabels(months_labels, rotation=45)
    #ax1.set_xticklabels(relative_labels, rotation=0)
    highlight_indices = [21, 22, 23, 24]
    for idx in highlight_indices:
        ax1.get_xticklabels()[idx].set_color('darkred')    
    
    ax1.set_xlabel("Months before and after the event")
    ax1.set_ylabel("Standardized anomalies")
    ax1.set_xlim(0, 30)
    ax1.grid(axis='y', alpha=0.3)
    ax1.axvline(x=21, linestyle='dashed', linewidth=0.5, alpha=0.5, color='k')  # Marzo evento
    ax1.axvline(x=24, linestyle='dashed', linewidth=0.5, alpha=0.5, color='k')  # Marzo evento
    ax1.axhline(y=0, linewidth=0.5, color='brown')
    ax1.axvspan(xmin=21, xmax=24, color='coral', alpha=0.1)

    # # Linee orizzontali per tutti i decimi tra 0 e 1 (sia positivi che negativi)
    # for y in np.arange(-1.0, 1.1, 0.1):
    #     if abs(y) > 1e-8:  # evita di sovrascrivere la linea y=0 già presente
    #         ax1.axhline(fwd(y), linewidth=0.3, color='brown', alpha=0.3, zorder=0)

    # ax1.scatter(x_Mar, fwd(MLD_Mar_anomalies_standardized), color='orange', marker='s', s=100)
    # for i in range(len(x_Mar)):
    #     label = f"MLD = {MLD_Mar_anomalies_standardized[i]:.2f}"
    #     ax1.text(x_Mar[i]+1.8, fwd(MLD_Mar_anomalies_standardized[i])-0.2, label, ha='center', fontsize=10, color='k')

    ax1.set_yscale('function', functions=(fwd, inv))
    yticks = np.linspace(-5, 5, 11)
    ax1.yaxis.set_major_locator(FixedLocator(fwd(yticks)))
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda val, pos: f"{inv(val):.0f}"))
    ax1.set_ylim(fwd(-5), fwd(5))

    #ax1.legend(loc='upper left')

    ax1.legend(
        handles=[split_handle, line_handle],
        labels=['NAO', r'$\Delta F$'],
        handler_map={split_handle: SplitLegendHandler()},
        loc='upper left'
    )
    plt.title("NAO and Labrador Sea surface heat flux anomalies before and after shallow convection events")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_rho_ts(output_path):
    x_smooth, rho_smooth = smooth_data(x, Drho_mean)
    _, T_smooth = smooth_data(x, Drho_T_mean)
    _, S_smooth = smooth_data(x, Drho_S_mean)

    _, rho_std_smooth = smooth_data(x, Drho_std)
    _, T_std_smooth = smooth_data(x, Drho_T_std)
    _, S_std_smooth = smooth_data(x, Drho_S_std)

    fig, ax1 = plt.subplots(figsize=(10, 6))

    ax1.plot(x_smooth, fwd(rho_smooth), linestyle='-', color='brown', linewidth=2, label=r'$\Delta \rho$', zorder=1)
    ax1.plot(x_smooth, fwd(T_smooth), linestyle='-', color='blue', linewidth=2, label=r'-$\alpha \Delta T$', zorder=2)
    ax1.plot(x_smooth, fwd(S_smooth), linestyle='-', color='gray', linewidth=2, label=r'$\beta \Delta S$', zorder=3)

    ax1.fill_between(x_smooth, fwd(rho_smooth - rho_std_smooth), fwd(rho_smooth + rho_std_smooth), color='brown', alpha=0.2)
    ax1.fill_between(x_smooth, fwd(T_smooth - T_std_smooth), fwd(T_smooth + T_std_smooth), color='blue', alpha=0.2)
    ax1.fill_between(x_smooth, fwd(S_smooth - S_std_smooth), fwd(S_smooth + S_std_smooth), color='gray', alpha=0.1)

    ax1.set_xticks(x)
    ax1.set_xticklabels(months_labels, rotation=45)
    #ax1.set_xticklabels(relative_labels, rotation=0)
    highlight_indices = [21, 22, 23, 24]
    for idx in highlight_indices:
        ax1.get_xticklabels()[idx].set_color('darkred')    

    ax1.set_xlabel("Months before and after the event")
    ax1.set_ylabel("Standardized anomalies")
    ax1.set_xlim(0, 30)
    ax1.grid(axis='y', alpha=0.3)
    ax1.axvline(x=21, linestyle='dashed', linewidth=0.5, alpha=0.5, color='k')  # Marzo evento
    ax1.axvline(x=24, linestyle='dashed', linewidth=0.5, alpha=0.5, color='k')  # Marzo evento
    ax1.axhline(y=0, linewidth=0.5, color='brown')
    ax1.axvspan(xmin=21, xmax=24, color='coral', alpha=0.1)


    # ax1.scatter(x_Mar, fwd(MLD_Mar_anomalies_standardized), color='orange', marker='s', s=100)
    # for i in range(len(x_Mar)):
    #     label = f"MLD = {MLD_Mar_anomalies_standardized[i]:.2f}"
    #     ax1.text(x_Mar[i]+1.8, fwd(MLD_Mar_anomalies_standardized[i])-0.2, label, ha='center', fontsize=10, color='k')


    ax1.set_yscale('function', functions=(fwd, inv))
    yticks = np.linspace(-5, 5, 11)
    ax1.yaxis.set_major_locator(FixedLocator(fwd(yticks)))
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda val, pos: f"{inv(val):.0f}"))
    ax1.set_ylim(fwd(-6), fwd(6))

    ax1.legend(loc='upper left')
    plt.title("Labrador Sea surface density anomaly before and after shallow convection events")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

# === Esecuzione ===
plot_nao_df('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Bilanci_extended/Figure/evolution_multimodel_NAO_DF_extended_30.6_noMLD.png')
plot_rho_ts('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Bilanci_extended/Figure/evolution_multimodel_rho_TS_extended_30.6_noMLD.png')
