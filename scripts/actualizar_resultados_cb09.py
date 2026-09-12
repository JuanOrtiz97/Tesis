from pathlib import Path
import csv,json,datetime,statistics
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]
with (R/'datos/Datos Caso Base3.csv').open(encoding='utf-8-sig') as f:
 rows=list(csv.reader(f,delimiter=';'))
headers=rows[0];units=dict(zip(headers,rows[1]));dates=[datetime.datetime.strptime(x[0],'%d/%m/%Y') for x in rows[2:]]
D={k:np.array([float(x[j].replace(',','.')) for x in rows[2:]]) for j,k in enumerate(headers) if j}
assert len(dates)==365 and len(set(dates))==365 and all(np.isfinite(v).all() for v in D.values())
months=np.array([d.month for d in dates]);names=['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
def total(k):return float(D[k].sum())
def mean(k):return float(D[k].mean())
def f(x):return f'{x:.2f}'.replace('.',',')
def monthly(k):return np.array([D[k][months==m].mean() if units[k] in ['°C','ac/h'] else D[k][months==m].sum() for m in range(1,13)])
def datepeak(k):return dates[int(np.argmax(abs(D[k])))].strftime('%d/%m/%Y')
source=r'\fuente{Elaboración propia a partir de \texttt{Datos Caso Base3.csv}, exportado de la corrida 09 de DesignBuilder. Resultados provisionales.}'
def table(title,cols,rows,widths):
 s=r'\begin{table}[H]'+'\n'+r'\centering'+'\n'+r'\caption{'+title+'}\n'+r'{\small\singlespacing\renewcommand{\arraystretch}{1.2}'+'\n'+r'\begin{tabular}{'+widths+'}\n'+r'\toprule'+'\n'+' & '.join(cols)+r' \\'+'\n'+r'\midrule'+'\n'
 s+=''.join(' & '.join(row)+r' \\'+'\n' for row in rows)
 return s+r'\bottomrule'+'\n'+r'\end{tabular}}'+'\n'+source+'\n'+r'\end{table}'+'\n'
def fig(file,caption):return '\n'+r'\begin{figure}[H]'+'\n'+r'\centering'+'\n'+r'\includegraphics[width=\textwidth]{figuras/'+file+'.pdf}\n'+r'\caption{'+caption+'}\n'+source+'\n'+r'\end{figure}'+'\n'
syn=[('Enfriamiento sensible',f(-total('Sensible Cooling')),'kWh térmicos/año'),('Enfriamiento total',f(-total('Total Cooling')),'kWh térmicos/año'),('Electricidad de enfriamiento estimada',f(total('Cooling (Electricity)')),'kWh eléctricos/año'),('Electricidad de equipos',f(total('Room Electricity')),'kWh eléctricos/año'),('Electricidad de iluminación',f(total('Lighting')),'kWh eléctricos/año'),('Ganancia solar por ventanas exteriores',f(total('Solar Gains Exterior Windows')),'kWh/año'),('Máximo diario de enfriamiento sensible',f(max(-D['Sensible Cooling'])),'kWh/día; '+datepeak('Sensible Cooling')),('Temperatura operativa media',f(mean('Operative Temperature')),r'$^\circ$C'),('Máxima media diaria operativa',f(max(D['Operative Temperature'])),r'$^\circ$C'),('Días con media operativa mayor de 28 °C',str(int((D['Operative Temperature']>28).sum())),'días; indicador exploratorio'),('Ventilación e infiltración media',f(mean('Mech Vent + Nat Vent + Infiltration')),'renovaciones/hora')]
tex=table('Síntesis anual del caso base revisado',['Indicador','Valor','Unidad o alcance'],syn,'p{6.1cm}rp{4.5cm}')
tex+='\nLa electricidad de enfriamiento es una estimación de DesignBuilder bajo las eficiencias configuradas, no un consumo medido. El enfriamiento total incluye el sensible; ambas magnitudes no se suman. Las temperaturas corresponden a medias del edificio exportadas por el programa.\n\\clearpage\n'
mr=[[names[m]]+[f(monthly(k)[m]*sign) for k,sign in [('Cooling (Electricity)',1),('Sensible Cooling',-1),('Solar Gains Exterior Windows',1),('Operative Temperature',1),('Outside Dry-Bulb Temperature',1)]] for m in range(12)]
tex+=table('Resultados mensuales del caso base revisado',['Mes','Electricidad de enfriamiento','Enfriamiento sensible','Solar exterior',r'$T_{op}$',r'$T_{ext}$'],[['','kWh','kWh','kWh','°C','°C']]+mr,'lp{2.5cm}p{2.5cm}p{2.2cm}rr')
tex+=fig('caso-base-final-enfriamiento-mensual','Electricidad estimada y energía térmica de enfriamiento por mes')+'\\clearpage\n'
labels={'Glazing':'Acristalamientos','Walls':'Muros','Ceilings (int)':'Cielos interiores','Floors (int)':'Pisos interiores','Ground Floors':'Piso sobre terreno','Partitions (int)':'Particiones interiores','Roofs':'Cubiertas','Floors (ext)':'Pisos exteriores','Internal Natural vent.':'Ventilación natural interna','External Air':'Aire exterior','External Vent.':'Ventilación exterior','General Lighting':'Iluminación','Miscellaneous':'Misceláneos','Catering':'Cocina','Computer + Equip':'Computadores y equipos','Occupancy':'Ocupación','Solar Gains Interior Windows':'Solar por ventanas interiores','Solar Gains Exterior Windows':'Solar por ventanas exteriores','Zone Sensible Heating':'Calefacción sensible de zona','Zone Sensible Cooling':'Enfriamiento sensible de zona'}
bs=sorted(labels,key=lambda k:total(k),reverse=True)
tex+=table('Balance térmico anual por componentes del modelo revisado',['Componente','Balance (kWh)','Signo del intercambio'],[[labels[k],f(total(k)),'Ganancia neta' if total(k)>0 else 'Pérdida neta'] for k in bs],'p{6.2cm}rp{4cm}')
tex+='\nSe conserva la convención de signos del programa: positivo hacia el recinto y negativo desde él. Los intercambios entre zonas se muestran como términos del reporte; esta tabla no constituye un balance cerrado de todo el edificio. La electricidad de equipos no se agrega nuevamente a sus ganancias térmicas.\n\\clearpage\n'
tex+=fig('caso-base-final-balance-componentes','Balance general anual: aportes y extracciones de calor')+'\\clearpage\n'
tex+=fig('caso-base-final-temperatura-mensual','Temperaturas medias mensuales del edificio y del exterior')
tex+=fig('caso-base-temperatura-diaria','Evolución de las medias diarias de temperatura')+'\\clearpage\n'
tex+=fig('caso-base-ventilacion-mensual','Ventilación e infiltración: media mensual del edificio')
tex+=fig('caso-base-consumos-electricos','Distribución de la electricidad anual estimada')
(R/'insumos/caso-base-final-tablas.tex').write_text(tex,encoding='utf-8')
from estilo_graficos_uda import aplicar,guardar,TEAL
aplicar()
def save(name):guardar(R,name)
x=np.arange(12)
figg,axs=plt.subplots(2,1,figsize=(8,5.7),sharex=True)
axs[0].bar(x,monthly('Cooling (Electricity)'),color='#2D7F9D');axs[0].set_ylabel('Electricidad estimada (kWh)')
axs[1].bar(x-.18,-monthly('Sensible Cooling'),width=.36,label='Sensible',color='#1D3445');axs[1].bar(x+.18,-monthly('Total Cooling'),width=.36,label='Total',color='#7080A0');axs[1].set_ylabel('Energía térmica (kWh)');axs[1].legend(frameon=False,ncol=2);axs[1].set_xticks(x,names)
for ax in axs:ax.grid(axis='y',alpha=.16);ax.set_axisbelow(True)
save('caso-base-final-enfriamiento-mensual')
plt.figure(figsize=(8,7.2));vals=np.array([total(k)/1000 for k in bs]);plt.barh([labels[k] for k in bs],vals,color=['#C97728' if v>0 else TEAL for v in vals]);plt.gca().invert_yaxis();plt.axvline(0,color='#606A73',lw=.8);plt.xlabel('Balance anual (MWh térmicos)');plt.grid(axis='x',alpha=.15);save('caso-base-final-balance-componentes')
plt.figure(figsize=(8,3.7))
for k,l,c in [('Operative Temperature','Operativa','#1D3445'),('Air Temperature','Aire interior','#2D7F9D'),('Outside Dry-Bulb Temperature','Exterior','#C97728')]:plt.plot(x,monthly(k),marker='o',ms=4,label=l,color=c)
plt.xticks(x,names);plt.ylabel('Temperatura media (°C)');plt.legend(frameon=False,ncol=3);plt.grid(alpha=.15);save('caso-base-final-temperatura-mensual')
plt.figure(figsize=(8,3.7))
for k,l,c in [('Operative Temperature','Operativa','#1D3445'),('Outside Dry-Bulb Temperature','Exterior','#C97728')]:plt.plot(dates,D[k],label=l,color=c,lw=1)
plt.xticks([datetime.datetime(2025,m,1) for m in range(1,13)],names);plt.xlim(dates[0],dates[-1]);plt.ylabel('Media diaria (°C)');plt.legend(frameon=False);plt.grid(alpha=.15);save('caso-base-temperatura-diaria')
plt.figure(figsize=(8,3.5));plt.bar(x,monthly('Mech Vent + Nat Vent + Infiltration'),color='#2D7F9D');plt.xticks(x,names);plt.ylabel('Renovaciones de aire (h⁻¹)');plt.grid(axis='y',alpha=.15);save('caso-base-ventilacion-mensual')
plt.figure(figsize=(8,3.4));plt.barh(['Enfriamiento estimado','Equipos','Iluminación'],[total(k)/1000 for k in ['Cooling (Electricity)','Room Electricity','Lighting']],color=['#2D7F9D','#1D3445','#7080A0']);plt.xlabel('Electricidad anual (MWh)');plt.grid(axis='x',alpha=.15);save('caso-base-consumos-electricos')
summary={'annual':{k:total(k) for k in D if units[k]=='kWh'},'means':{k:mean(k) for k in D if units[k]!='kWh'},'op_daily_max':float(max(D['Operative Temperature'])),'days_op_gt28':int((D['Operative Temperature']>28).sum()),'peak_sensible_daily':float(max(-D['Sensible Cooling'])),'peak_date':datepeak('Sensible Cooling')}
(R/'insumos/caso-base09-diario-resumen.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=True))
