"""Estilo común de todos los gráficos cuantitativos de la tesis."""
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, ScalarFormatter
INK='#202A33'
BLUE='#2D7F9D'
DARK='#1D3445'
GRAY='#7080A0'
ORANGE='#C97728'
LIGHT='#B0C0D0'
MONTHS=['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
def aplicar():
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.labelsize':10,'xtick.labelsize':9,'ytick.labelsize':9,'legend.fontsize':9,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#606A73','axes.linewidth':.8,'lines.linewidth':1.1,'axes.labelcolor':INK,'text.color':INK,'xtick.color':INK,'ytick.color':INK,'pdf.fonttype':42,'figure.facecolor':'white','axes.facecolor':'white','savefig.facecolor':'white','axes.axisbelow':True,'grid.color':LIGHT,'grid.alpha':.25})
def guardar(root,nombre):
 fig=plt.gcf()
 for ax in fig.axes:
  if ax.name!='polar' and isinstance(ax.yaxis.get_major_formatter(),ScalarFormatter):
   ax.yaxis.set_major_formatter(FuncFormatter(lambda v,p: f'{v:g}'.replace('.',',')))
 fig.tight_layout(pad=1.2)
 for ext in ['pdf','png']:fig.savefig(root/'figuras'/f'{nombre}.{ext}',dpi=250,bbox_inches=None)
 plt.close(fig)
