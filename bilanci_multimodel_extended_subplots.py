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

# === Etichette mesi per 31 mesi ===
months_labels = [
    "Mar$_{-2}$", "Apr", "May", "Jun", "Jul", "Aug", 
    "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar$_{-1}$",
    "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    "Jan", "Feb", "Mar$_{0}$", "Apr", "May", "Jun", "Jul", "Aug", "Sep"
]
x = np.arange(31)  # 0...30
x_Mar = np.array([0, 12, 24])
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

# === Custom handler per NAO split legend ===
class SplitLegendHandle:
    def __init__(self, color_left='darkred', color_right='blue'):
        self.color_left = color_left
        self.color_right = color_right

class SplitLegendHandler(HandlerBase):
    def create_artists(self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans):
        r1 = Rectangle([xdescent, ydescent], width/2, height,
                       facecolor=orig_handle.color_left, edgecolor='k', lw=0.5, alpha=0.4, transform=trans)
        r2 = Rectangle([xdescent + width/2, ydescent], width/2, height,
                       facecolor=orig_handle.color_right, edgecolor='k', lw=0.5, alpha=0.4, transform=trans)
        return [r1, r2]

def plot_combined(output_path):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 11), sharex=True)

    # === Prima subplot: NAO e DF ===
    x_smooth, F_smooth = smooth_data(x, DF_mean)
    _, F_std_smooth = smooth_data(x, DF_std)

    colors = ['blue' if val < 0 else 'darkred' for val in NAO_mean]
    nao_transformed = fwd(NAO_mean)
    nao_err_upper = fwd(NAO_mean + NAO_std)
    nao_err_lower = fwd(NAO_mean - NAO_std)
    nao_err = [nao_transformed - nao_err_lower, nao_err_upper - nao_transformed]

    ax1.bar(x, nao_transformed, color=colors, alpha=0.4, label='NAO', zorder=0)
    ax1.errorbar(x, nao_transformed, yerr=nao_err, fmt='none', ecolor='k', capsize=3, elinewidth=1, alpha=0.9, zorder=1)
    line_handle = ax1.plot(x_smooth, fwd(F_smooth), linestyle='dotted', color='k', linewidth=2, label=r'$\Delta F$', zorder=2)[0]
    ax1.fill_between(x_smooth, fwd(F_smooth - F_std_smooth), fwd(F_smooth + F_std_smooth), color='black', alpha=0.1)

    ax1.scatter(x_Mar, fwd(MLD_Mar_anomalies_standardized), color='orange', marker='s', s=100, label='MLD')
    for i in range(len(x_Mar)):
        ax1.text(x_Mar[i]+1.4, fwd(MLD_Mar_anomalies_standardized[i])-0.2,
             f"$\\Delta$MLD={MLD_Mar_anomalies_standardized[i]:.2f}", ha='center', fontsize=10, color='k')

    ax1.set_ylabel("Standardized anomalies")
    ax1.set_xlim(0, 30)
    ax1.set_yscale('function', functions=(fwd, inv))
    yticks = np.linspace(-5, 5, 11)
    ax1.yaxis.set_major_locator(FixedLocator(fwd(yticks)))
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda val, pos: f"{inv(val):.0f}"))
    ax1.set_ylim(fwd(-5), fwd(5))
    ax1.grid(axis='y', alpha=0.3)
    ax1.axhline(y=0, linewidth=0.5, color='brown')
    ax1.axvline(x=21, linestyle='dashed', linewidth=0.5, color='k')
    ax1.axvline(x=24, linestyle='dashed', linewidth=0.5, color='k')
    ax1.axvspan(21, 24, color='coral', alpha=0.1)
    ax1.set_xticks(x)
    ax1.set_xticklabels(months_labels, rotation=45)
    ax1.tick_params(axis='x', labelbottom=True)
    # Colora i tick di interesse
    for idx, label in enumerate(ax1.get_xticklabels()):
        if idx in [21, 22, 23, 24]:
            label.set_color('darkred')

    ax1.legend(
        handles=[SplitLegendHandle(), line_handle],
        labels=['NAO index', r'$\Delta F$'],
        handler_map={SplitLegendHandle: SplitLegendHandler()},
        loc='upper left'
    )

    # === Seconda subplot: rho, T, S ===
    x_smooth, rho_smooth = smooth_data(x, Drho_mean)
    _, T_smooth = smooth_data(x, Drho_T_mean)
    _, S_smooth = smooth_data(x, Drho_S_mean)
    _, rho_std_smooth = smooth_data(x, Drho_std)
    _, T_std_smooth = smooth_data(x, Drho_T_std)
    _, S_std_smooth = smooth_data(x, Drho_S_std)

    ax2.plot(x_smooth, fwd(rho_smooth), linestyle='-', color='brown', linewidth=2, label=r'$\Delta \rho$', zorder=1)
    ax2.plot(x_smooth, fwd(T_smooth), linestyle='-', color='blue', linewidth=2, label=r'-$\alpha \Delta T$', zorder=2)
    ax2.plot(x_smooth, fwd(S_smooth), linestyle='-', color='gray', linewidth=2, label=r'$\beta \Delta S$', zorder=3)
    ax2.fill_between(x_smooth, fwd(rho_smooth - rho_std_smooth), fwd(rho_smooth + rho_std_smooth), color='brown', alpha=0.2)
    ax2.fill_between(x_smooth, fwd(T_smooth - T_std_smooth), fwd(T_smooth + T_std_smooth), color='blue', alpha=0.2)
    ax2.fill_between(x_smooth, fwd(S_smooth - S_std_smooth), fwd(S_smooth + S_std_smooth), color='gray', alpha=0.1)

    ax2.scatter(x_Mar, fwd(MLD_Mar_anomalies_standardized), color='orange', marker='s', s=100)
    for i in range(len(x_Mar)):
        ax2.text(x_Mar[i]+1.4, fwd(MLD_Mar_anomalies_standardized[i])-0.2,
             f"$\\Delta$MLD={MLD_Mar_anomalies_standardized[i]:.2f}", ha='center', fontsize=10, color='k')

    ax2.set_xticks(x)
    ax2.set_xticklabels(months_labels, rotation=45)
    for idx, label in enumerate(ax2.get_xticklabels()):
        if idx in [21, 22, 23, 24]:
            label.set_color('darkred')

    ax2.set_xlim(0, 30)
    ax2.set_xlabel("Months before and after the event")
    ax2.set_ylabel("Standardized anomalies")
    ax2.set_yscale('function', functions=(fwd, inv))
    ax2.yaxis.set_major_locator(FixedLocator(fwd(yticks)))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda val, pos: f"{inv(val):.0f}"))
    ax2.set_ylim(fwd(-5), fwd(5))
    ax2.grid(axis='y', alpha=0.3)
    ax2.axhline(y=0, linewidth=0.5, color='brown')
    ax2.axvline(x=21, linestyle='dashed', linewidth=0.5, color='k')
    ax2.axvline(x=24, linestyle='dashed', linewidth=0.5, color='k')
    ax2.axvspan(21, 24, color='coral', alpha=0.1)
    ax2.legend(loc='upper left')

    ax1.text(0, 1.05, 'a)', transform=ax1.transAxes, fontsize=12, fontweight='semibold', va='top')
    ax2.text(0, 1.05, 'b)', transform=ax2.transAxes, fontsize=12, fontweight='semibold', va='top')

    # === Titolo unico ===
    fig.suptitle("Labrador Sea surface heat and density anomalies before and after shallow convection events", fontsize=16, y=0.98)

    plt.tight_layout()  # lascia spazio per il titolo
    plt.savefig(output_path, dpi=300)
    plt.close()

plot_combined('/home/buccellato/work_big/SPG/PCONTROL/CODICI/MULTIMODEL/Bilanci_extended/Figure/evolution_multimodel_extended_subplots_15.1.26.png')
