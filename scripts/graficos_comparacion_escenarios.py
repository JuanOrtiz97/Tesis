from pathlib import Path
import sys,json,shutil,hashlib
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
R=Path(__file__).resolve().parents[1]
P=Path(__file__).parent
sys.path.insert(0,str(R/'scripts'))
from estilo_graficos_uda import aplicar,BLUE,DARK,GRAY,ORANGE,TEAL,MONTHS
aplicar()
F=R/'figuras/escenarios';F.mkdir(exist_ok=True)
def es(v,n=2):return f'{v:,.{n}f}'.replace(',','_').replace('.',',').replace('_','.')
annual={};monthly={}
for case in ['C1','C2','C3']:
 a=pd.read_csv(R/'datos'/f'{case.lower()}-comparacion-enfriamiento-anual.csv')
 m=pd.read_csv(R/'datos'/f'{case.lower()}-comparacion-enfriamiento-mensual.csv')
 annual[case]=a[case].sum();monthly[case]=m.groupby('mes')[case].sum()
 annual['CB']=a.CB.sum();monthly['CB']=m.groupby('mes').CB.sum()
df=pd.read_csv(R/'datos/comparacion-cuatro-escenarios.csv')
colors={'CB':GRAY,'C1':BLUE,'C2':ORANGE,'C3':DARK};styles={'CB':'--','C1':'-','C2':':','C3':'-.'};markers={'CB':'o','C1':'s','C2':'^','C3':'D'}
fig,axs=plt.subplots(2,1,figsize=(8,6.4),gridspec_kw={'height_ratios':[1,1.15]})
for i,case in enumerate(df.caso):
 axs[0].barh(i,annual[case]/1000,color=colors[case],height=.6)
 axs[0].text(annual[case]/1000+1,i,es(annual[case]/1000)+' MWh',va='center')
axs[0].set_yticks(range(4),df.caso);axs[0].invert_yaxis();axs[0].set_xlim(0,100);axs[0].set_xlabel('Demanda anual de enfriamiento (MWh térmicos)');axs[0].grid(axis='x')
for case in ['CB','C1','C2','C3']:axs[1].plot(range(1,13),monthly[case]/1000,color=colors[case],ls=styles[case],marker=markers[case],ms=4,label=case)
axs[1].set_xticks(range(1,13),MONTHS);axs[1].set_ylabel('Demanda mensual (MWh térmicos)');axs[1].grid(axis='y');axs[1].legend(frameon=False,ncol=4,loc='lower center',bbox_to_anchor=(.5,1.02))
for ax in axs:ax.xaxis.set_major_formatter(FuncFormatter(lambda v,p:es(v,0))) if ax==axs[0] else None;ax.yaxis.set_major_formatter(FuncFormatter(lambda v,p:es(v,0))) if ax==axs[1] else None
fig.tight_layout(pad=1.25,h_pad=2)
for ext in ['pdf','png']:fig.savefig(F/f'comparacion-anual-mensual.{ext}',dpi=250)
plt.close(fig)
fig,ax=plt.subplots(figsize=(8,3.8))
for i,case in enumerate(['C1','C2','C3']):
 delta=(monthly[case]-monthly['CB'])/monthly['CB']*100
 ax.plot(range(1,13),delta,label=case,c=colors[case],ls=styles[case],marker=markers[case],ms=4)
ax.axhline(0,c=GRAY,lw=.8);ax.set_xticks(range(1,13),MONTHS);ax.set_ylabel('Variación mensual respecto a CB (%)');ax.yaxis.set_major_formatter(FuncFormatter(lambda v,p:es(v,1)));ax.grid(axis='y');ax.legend(ncol=3,frameon=False,loc='lower center',bbox_to_anchor=(.5,1.02));fig.tight_layout()
for ext in ['pdf','png']:fig.savefig(F/f'variacion-mensual.{ext}',dpi=250)
plt.close(fig)
