from pathlib import Path
import re,sys,subprocess,shutil,json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap,TwoSlopeNorm
from matplotlib.ticker import FuncFormatter
R=Path(__file__).resolve().parents[1]
P=Path(__file__).parent
sys.path.insert(0,str(R/'scripts'))
from estilo_graficos_uda import aplicar,BLUE,DARK,GRAY,ORANGE,TEAL,MONTHS
aplicar()
def es(v,n=1):return f'{v:,.{n}f}'.replace(',','_').replace('.',',').replace('_','.')
def zona(z):
 f,n=z.split(':');return {'PLANTABAJA':'PB','PRIMERAPLANTAALTA':'1PA','SEGUNDAPLANTAALTA':'2PA','CUBIERTA':'CUB'}[f]+'-ASC' if n=='ASCENSOR' else n.replace('X','-')
def save(fig,path):
 for ax in fig.axes:
  if ax.name!='polar':ax.yaxis.set_major_formatter(FuncFormatter(lambda v,p:es(v,0)))
 fig.tight_layout(pad=1.25)
 for ext in ['pdf','png']:fig.savefig(path.with_suffix('.'+ext),dpi=250)
 plt.close(fig)
a=pd.read_csv(R/'datos/c1-comparacion-enfriamiento-anual.csv').set_index('zona')
m=pd.read_csv(R/'datos/c1-comparacion-enfriamiento-mensual.csv')
cmap=LinearSegmentedColormap.from_list('cambios',[TEAL,'white',ORANGE]);cmap.set_bad('#EEEEEE')
active=a.index[a.CB>1]
values=m.pivot(index='zona',columns='mes',values='variacion_pct').reindex(active).values
lim=max(5,np.ceil(np.nanmax(abs(values))/5)*5)
fig,ax=plt.subplots(figsize=(8,5.4))
im=ax.imshow(values,cmap=cmap,norm=TwoSlopeNorm(0,-lim,lim),aspect='auto')
ax.set_xticks(range(12),MONTHS);ax.set_yticks(range(len(active)),[zona(z) for z in active]);ax.tick_params(length=0)
for i in range(len(active)):
 for j in range(12):ax.text(j,i,es(values[i,j]),ha='center',va='center',fontsize=9,color='white' if abs(values[i,j])>.7*lim else DARK)
ax.set_xticks(np.arange(-.5,12,1),minor=True);ax.set_yticks(np.arange(-.5,len(active),1),minor=True);ax.grid(which='minor',color='white',lw=2);ax.tick_params(which='minor',length=0)
for sp in ax.spines.values():sp.set_visible(False)
cb=fig.colorbar(im,ax=ax,orientation='horizontal',pad=.13,aspect=35);cb.set_label('Variación respecto a CB (%) · turquesa: reducción · naranja: aumento')
fig.tight_layout();fig.savefig(R/'figuras/c1/02-matriz-mensual.pdf');plt.close(fig)
off=[z for z in a.index if '-OF-' in zona(z)]
fig,ax=plt.subplots(figsize=(8,4.4));y=np.arange(len(off));v=a.loc[off]
ax.hlines(y,v.C1,v.CB,color=TEAL,lw=2);ax.scatter(v.CB,y,c=GRAY,label='CB',marker='o',s=40);ax.scatter(v.C1,y,c=BLUE,label='C1',marker='D',s=35)
ax.set_yticks(y,[zona(z) for z in off]);ax.invert_yaxis();ax.set_xlim(0,v.CB.max()*1.24);ax.set_xlabel('Demanda anual de enfriamiento (kWh térmicos)');ax.legend(loc='lower center',bbox_to_anchor=(.5,1.02),ncol=2,frameon=False);ax.grid(axis='x')
for i,(_,r) in enumerate(v.iterrows()):ax.text(v.CB.max()*1.06,i,es(r.variacion_pct)+' %',va='center',color=TEAL)
fig.tight_layout();fig.savefig(R/'figuras/c1/03-cambio-oficinas.pdf');plt.close(fig)
fig,ax=plt.subplots(figsize=(8,4.2))
for mo in range(1,13):
 v=m.loc[m.mes==mo,'diferencia_kWh'];up=int((v>.1).sum());down=int((v<-.1).sum());zero=len(v)-up-down
 ax.scatter([mo]*up,range(1,up+1),c=ORANGE,s=26);ax.scatter([mo]*down,-np.arange(1,down+1),c=TEAL,s=26);ax.text(mo,.3,str(zero),ha='center',fontsize=9,color=GRAY)
ax.axhline(0,c=GRAY,lw=.8);ax.set_xticks(range(1,13),MONTHS);ax.set_ylabel('Número de zonas\naumento (+) / reducción (−)');ax.grid(axis='y');save(fig,R/'figuras/c1/04-zonas-por-mes')
# Homologar los cinco esquemas originales, conservando su geometría y contenido técnico.
for p in (R/'figuras/c1').glob('c1-*.tex'):
 s=p.read_text(encoding='utf-8').replace(r'\usepackage{lmodern}',r'\usepackage{mathptmx}').replace(r'\sffamily',r'\rmfamily')
 s=s.replace('PROPUESTA C1 ·','CRITERIO C1 ·').replace(r'20\,\% a ensayar',r'20\,\% simulado').replace(r'20\,\% propuesto para ensayo.',r'20\,\% aplicado en oficinas.')
 if p.stem=='c1-control-ventilacion':
  s=s.replace('Secuencia de control por verificar','Control térmico aplicado en seis oficinas')
  s=s.replace('El esquema no acredita que estos controles estén activos en el modelo.','Control por temperatura y modo mixto activos; intervalo exterior de 20 a 26 grados Celsius.')
 p.write_text(s,encoding='utf-8')
 result=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',p.name],cwd=p.parent,capture_output=True)
 assert result.returncode==0,result.stdout[-3000:]
print('C1: tres gráficos y cinco esquemas actualizados.')
