from pathlib import Path
import csv,datetime
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from estilo_graficos_uda import *
R=Path(__file__).resolve().parents[1]
rows=list(csv.reader(next((R/'datos').glob('*.epw')).open(encoding='latin1')))[8:]
assert len(rows)==8760
D={i:np.array([float(r[i]) for r in rows]) for i in [1,3,6,7,8,13,14,15,20,21,22,33]}
month=D[1].astype(int);x=np.arange(12)
mean=lambda i:np.array([D[i][month==m].mean() for m in range(1,13)])
aplicar()
def base(ylabel):
 plt.figure(figsize=(8,3.7));plt.xticks(x,MONTHS);plt.ylabel(ylabel);plt.grid(axis='y')
def save(n):guardar(R,'epw-uniforme-'+n)
# Daily temperature retains original daily resolution.
daily=D[6].reshape(365,24);dates=[datetime.datetime(2025,1,1)+datetime.timedelta(days=i) for i in range(365)]
plt.figure(figsize=(8,3.7));plt.fill_between(dates,daily.min(1),daily.max(1),color=LIGHT,alpha=.45,label='Rango diario');plt.plot(dates,daily.mean(1),color=ORANGE,label='Media diaria');plt.xticks([datetime.datetime(2025,m,1) for m in range(1,13)],MONTHS);plt.xlim(dates[0],dates[-1]);plt.ylabel('Temperatura exterior (°C)');plt.grid(axis='y');plt.legend(frameon=False,ncol=2);save('temperatura')
base('Humedad relativa (%)');plt.fill_between(x,[D[8][month==m].min() for m in range(1,13)],[D[8][month==m].max() for m in range(1,13)],color=LIGHT,alpha=.45,label='Mínima–máxima');plt.plot(x,mean(8),color=BLUE,marker='o',ms=4,label='Media');plt.ylim(0,105);plt.legend(frameon=False,ncol=2);save('humedad')
base('Punto de rocío (°C)');plt.fill_between(x,[D[7][month==m].min() for m in range(1,13)],[D[7][month==m].max() for m in range(1,13)],color=LIGHT,alpha=.45,label='Mínimo–máximo');plt.plot(x,mean(7),color=BLUE,marker='o',ms=4,label='Media');plt.legend(frameon=False,ncol=2);save('punto-rocio')
base('Radiación acumulada (kWh/m²·mes)')
for i,(col,label,color) in enumerate([(13,'Global horizontal',ORANGE),(14,'Directa normal',DARK),(15,'Difusa horizontal',BLUE)]):plt.bar(x+(i-1)*.25,[D[col][month==m].sum()/1000 for m in range(1,13)],width=.25,label=label,color=color)
plt.legend(frameon=False,ncol=3);save('radiacion-solar')
f,axs=plt.subplots(2,1,figsize=(8,5.6),sharex=True);axs[0].bar(x,mean(22),color=GRAY);axs[0].set_ylabel('Cobertura de cielo (décimas)');axs[0].set_ylim(0,10);axs[1].bar(x,[D[33][month==m].sum() for m in range(1,13)],color=BLUE);axs[1].set_ylabel('Precipitación (mm/mes)');axs[1].set_xticks(x,MONTHS)
for ax in axs:ax.grid(axis='y')
save('cielo-precipitacion')
base('Velocidad del viento (m/s)');plt.bar(x,[D[21][month==m].max() for m in range(1,13)],color=LIGHT,label='Máxima');plt.plot(x,mean(21),color=BLUE,marker='o',ms=4,label='Media');plt.legend(frameon=False,ncol=2);save('viento-mensual')
base('Amplitud térmica diaria (°C)');dm=month.reshape(365,24)[:,0];amp=np.ptp(daily,axis=1);plt.bar(x,[amp[dm==m].max() for m in range(1,13)],color=LIGHT,label='Máxima diaria');plt.plot(x,[amp[dm==m].mean() for m in range(1,13)],color=ORANGE,marker='o',ms=4,label='Media diaria');plt.legend(frameon=False,ncol=2);save('amplitud-termica')
fig,ax=plt.subplots(figsize=(8,4.8),subplot_kw={'projection':'polar'});bins=((D[20]+11.25)//22.5).astype(int)%16;freq=np.bincount(bins,minlength=16)/len(rows)*100;theta=np.arange(16)*np.pi/8;ax.bar(theta,freq,width=np.pi/10,color=BLUE);ax.set_theta_zero_location('N');ax.set_theta_direction(-1);ax.set_xticks(theta,['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSO','SO','OSO','O','ONO','NO','NNO']);ax.set_ylabel('Frecuencia horaria (%)',labelpad=35);ax.grid(alpha=.3);save('rosa-vientos')
grid=np.array([[D[6][(month==m)&(D[3]==h)].mean() for h in range(1,25)] for m in range(1,13)])
fig,ax=plt.subplots(figsize=(8,4.5));im=ax.imshow(grid,aspect='auto',cmap=LinearSegmentedColormap.from_list('uda',[BLUE,'#F3F5F7',ORANGE]));ax.set_yticks(x,MONTHS);ax.set_xticks([0,5,11,17,23],[1,6,12,18,24]);ax.set_xlabel('Hora local del archivo climático');fig.colorbar(im,ax=ax,label='Temperatura media (°C)',pad=.025);save('mapa-horario-temperatura')
print('9 gráficos climáticos actualizados desde 8760 registros')
