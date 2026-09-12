"""Sistema gráfico común: tipografía del documento y jerarquía sin solapamientos."""
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, ScalarFormatter
INK='#202A33'
BLUE='#2D7F9D'
DARK='#1D3445'
GRAY='#7080A0'
ORANGE='#C97728'
TEAL='#2A9D8F'
LIGHT='#B0C0D0'
MONTHS=['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']

def aplicar():
    plt.rcParams.update({
        'font.family':'serif','font.serif':['Times New Roman','DejaVu Serif'],
        'font.size':11,'axes.labelsize':11,'xtick.labelsize':10,
        'ytick.labelsize':10,'legend.fontsize':10,
        'axes.spines.top':False,'axes.spines.right':False,
        'axes.edgecolor':'#606A73','axes.linewidth':.8,'lines.linewidth':1.2,
        'axes.labelcolor':INK,'text.color':INK,'xtick.color':INK,'ytick.color':INK,
        'pdf.fonttype':42,'ps.fonttype':42,'figure.facecolor':'white',
        'axes.facecolor':'white','savefig.facecolor':'white','axes.axisbelow':True,
        'grid.color':LIGHT,'grid.alpha':.3,'grid.linewidth':.6,
        'axes.labelpad':8,'xtick.major.pad':5,'ytick.major.pad':5,
        'legend.handlelength':1.8,'legend.columnspacing':1.5,
    })

def guardar(root,nombre):
    fig=plt.gcf()
    for ax in fig.axes:
        if ax.name!='polar' and isinstance(ax.yaxis.get_major_formatter(),ScalarFormatter):
            ax.yaxis.set_major_formatter(FuncFormatter(lambda v,p: f'{v:g}'.replace('.',',')))
        legend=ax.get_legend()
        if legend is not None:
            handles,labels=ax.get_legend_handles_labels()
            legend.remove()
            ax.legend(handles,labels,loc='lower center',bbox_to_anchor=(.5,1.02),
                      ncol=min(3,len(labels)),frameon=False,borderaxespad=0)
        ax.tick_params(axis='both',which='major',width=.6)
    fig.tight_layout(pad=1.25,h_pad=2)
    for ext in ['pdf','png']:
        fig.savefig(root/'figuras'/f'{nombre}.{ext}',dpi=250,bbox_inches=None)
    plt.close(fig)
