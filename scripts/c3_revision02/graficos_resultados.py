from pathlib import Path
import sys,json,shutil
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

P=Path('C:/Users/juand/Documents/New project 3/Tesis-limpia/output/C3-revision02')
R=Path('C:/Users/juand/Desktop/Tesis de Maestria - Juan Ortiz/01_Documento_tesis/Repositorios/Trabajo_completo/Tesis-limpia')
sys.path.insert(0,str(R/'scripts'))
from estilo_graficos_uda import aplicar,BLUE,DARK,GRAY,TEAL,ORANGE,MONTHS
aplicar()
T=P/'tablas-y-graficos'; F=R/'figuras/escenarios';F.mkdir(exist_ok=True)
a=pd.read_csv(T/'comparacion-enfriamiento-anual.csv')
m=pd.read_csv(T/'comparacion-enfriamiento-mensual.csv').groupby('mes')[['CB','C3']].sum()
old=pd.read_csv(R/'datos/comparacion-cuatro-escenarios.csv')
old['caso']=old.caso.replace({'C3':'C3 r01'})
cb=float(a.CB.sum()); c3=float(a.C3.sum()); reduction=100*(cb-c3)/cb
new=pd.concat([old,pd.DataFrame([{'caso':'C3 r02','enfriamiento_total_kWh_termicos':c3,'diferencia_CB_kWh':c3-cb,'variacion_CB_pct':-reduction}])],ignore_index=True)
new.to_csv(R/'datos/comparacion-escenarios-C3r02.csv',index=False,encoding='utf-8-sig')
for source,target in [('comparacion-enfriamiento-anual.csv','C3r02-enfriamiento-anual-por-zona.csv'),('comparacion-enfriamiento-mensual.csv','C3r02-enfriamiento-mensual-por-zona.csv'),('C3-todas-variables-mensuales-anuales.csv','C3r02-variables-mensuales-anuales.csv')]:
    shutil.copy2(T/source,R/'datos'/target)

fig,axs=plt.subplots(2,1,figsize=(7.2,7.6),gridspec_kw={'height_ratios':[1,1.35]})
colors=[DARK,GRAY,ORANGE,BLUE,TEAL]
values=new.enfriamiento_total_kWh_termicos/1000
axs[0].barh(new.caso,values,color=colors,height=.6)
axs[0].invert_yaxis();axs[0].set_xlim(0,max(values)*1.18)
axs[0].set_xlabel('Demanda total de enfriamiento (MWh térmicos/año)')
for y,v in enumerate(values):axs[0].text(v+.7,y,f'{v:.2f}'.replace('.',','),va='center',fontsize=10)
axs[0].grid(axis='x');axs[0].set_title('a. Evolución de los ensayos',loc='left',fontsize=12,pad=12)
for col,label,color,marker in [('CB','Caso base',DARK,'o'),('C3','C3 revisión 02',TEAL,'s')]:
    axs[1].plot(range(1,13),m[col]/1000,label=label,color=color,marker=marker,markersize=4)
axs[1].set_xticks(range(1,13),MONTHS);axs[1].set_ylabel('MWh térmicos/mes');axs[1].set_ylim(bottom=0);axs[1].grid(axis='y')
axs[1].legend(loc='upper right',frameon=False);axs[1].set_title('b. Distribución mensual',loc='left',fontsize=12,pad=12)
fig.tight_layout(h_pad=2.1)
for ext in ['pdf','png']:fig.savefig(F/f'C3r02-comparacion.{ext}',dpi=300)
plt.close(fig)

z=a[(a.CB>1e-5)|(a.C3>1e-5)].copy().sort_values('CB')
z['nombre']=z.zona.str.split(':').str[-1].str.replace('X','-',regex=False)
fig,ax=plt.subplots(figsize=(7.2,5.5))
y=np.arange(len(z));ax.hlines(y,z.CB/1000,z.C3/1000,color='#B0C0D0',lw=2)
ax.scatter(z.CB/1000,y,color=DARK,label='Caso base',s=28)
ax.scatter(z.C3/1000,y,color=TEAL,label='C3 revisión 02',marker='s',s=25)
ax.set_yticks(y,z.nombre);ax.set_xlabel('Demanda total de enfriamiento (MWh térmicos/año)');ax.set_xlim(left=0)
ax.grid(axis='x');ax.legend(loc='lower right',frameon=False);fig.tight_layout()
for ext in ['pdf','png']:fig.savefig(F/f'C3r02-zonas.{ext}',dpi=300)
plt.close(fig)
summary={'CB_kWh_termicos':cb,'C3r02_kWh_termicos':c3,'reduccion_pct':reduction,'reduccion_kWh_termicos':cb-c3,'diferencia_C3r01_kWh':c3-float(old.iloc[-1].enfriamiento_total_kWh_termicos),'zonas_con_enfriamiento':len(z)}
(P/'resumen-resultados.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary))
