from pathlib import Path
import re,csv,math
import numpy as np,pandas as pd
R=Path(r'C:\Users\juand\Desktop\Tesis de Maestria - Juan Ortiz\01_Documento_tesis\Repositorios\Trabajo_completo\Tesis-limpia');W=Path(r'C:\Users\juand\Documents\New project 3\Tesis-limpia\output')
s=(R/'datos/db-caso-base-revision09.idf').read_text(encoding='utf-8-sig');a=[[x.strip() for x in t.split(',')] for t in re.sub(r'!.*','',s).split(';')]
assert float(next(x for x in a if x[0].lower()=='building')[2])==0
assert all(float(x[2])==0 for x in a if x[0].lower()=='zone')
def geom(p,start):
 v=np.array(list(map(float,p[start:]))).reshape(-1,3);n=np.cross(v,np.roll(v,-1,axis=0)).sum(axis=0)/2
 return float(np.linalg.norm(n)),(math.degrees(math.atan2(n[0],n[1]))+360)%360
sur={p[1]:p for p in a if p[0].lower()=='buildingsurface:detailed'}
orient=['N','NE','E','SE','S','SO','O','NO'];rows=[];walls=[]
for name,p in sur.items():
 if p[2].lower()=='wall' and p[5].lower()=='outdoors':
  ar,az=geom(p,11);walls.append({'superficie':name,'orientacion':orient[int((az+22.5)//45)%8],'area_m2':ar})
for p in a:
 if p[0].lower()!='fenestrationsurface:detailed' or p[2].lower()!='window':continue
 parent=sur[p[4]]
 if parent[5].lower()!='outdoors':continue
 area,az=geom(p,10);area*=float(p[8] or 1)
 rows.append({'superficie':p[1],'construccion':p[3].upper(),'orientacion':orient[int((az+22.5)//45)%8],'area_m2':area,'padre':p[4]})
df=pd.DataFrame(rows);wf=pd.DataFrame(walls);df.to_csv(R/'datos/revision-ventanas-exteriores.csv',index=False)
by=wf.groupby('orientacion').area_m2.sum().to_frame('muro_bruto_m2').join(df.groupby('orientacion').area_m2.sum().rename('ventana_m2')).fillna(0);by['WWR_pct']=by.ventana_m2/by.muro_bruto_m2*100;by=by.reindex([o for o in orient if o in by.index]);by.to_csv(R/'datos/revision-WWR-orientacion.csv')
opt={}
with (W/'caso-base-revision-2026-09-12/corrida-09-cargas-estabilidad/eplusout.eio').open() as f:
 for row in csv.reader(f):
  if row and row[0].strip()=='WindowConstruction':opt[row[1].strip()]=list(map(float,[row[5],row[6],row[8]]))
def fmt(v):return f'{v:.2f}'.replace('.',',')
text=r'''\clearpage
\subsection{Acristalamiento y proporción de ventana por orientación}
Las superficies transparentes exteriores se extraen de los objetos FenestrationSurface:Detailed y se vinculan con su muro exterior. Se excluyen ventanas interiores, puertas, rejillas y huecos de paso. La relación ventana-muro (WWR) utiliza el área bruta del muro como denominador y el polígono modelado de ventana como numerador; no es área libre de ventilación. Las orientaciones agrupan sectores de 45 grados respecto al norte del modelo.
\begin{table}[H]\centering\caption{Ventanas exteriores y propiedades ópticas del caso base}
{\small\singlespacing\begin{tabular}{p{4.6cm}rrrr}\toprule
Construcción & Área (m$^2$) & U reportada & SHGC & VT \\ \midrule
'''
for const,area in df.groupby('construccion').area_m2.sum().items():
 u,g,vt=opt[const];label='Vidrio claro de 6 mm' if '6MM' in const else 'Vidrio templado de 8 mm'
 text+=' & '.join([label,fmt(area),fmt(u),fmt(g),fmt(vt)])+r' \\'+'\n'
text+=r'''\bottomrule\end{tabular}}
\fuente{Elaboración propia a partir del IDF y WindowConstruction del EIO de la corrida 09. U en W/m$^2$K según reporte del vidrio; no acredita U del conjunto con marco ni puentes térmicos.}
\end{table}
\begin{table}[H]\centering\caption{Relación entre ventana y muro exterior por orientación}
{\small\singlespacing\begin{tabular}{lrrr}\toprule
Orientación & Muro bruto (m$^2$) & Ventana (m$^2$) & WWR (\%) \\ \midrule
'''
for o,row in by.iterrows():text+=' & '.join([o,*[fmt(v) for v in row]])+r' \\'+'\n'
text+=r'''\bottomrule\end{tabular}}
\fuente{Elaboración propia por cálculo de polígonos del IDF. Los CSV del expediente conservan las superficies y la agregación por orientación.}
\end{table}
La transmitancia unidimensional del muro se desarrolla en la sección anterior. C3 revisión 02 declara U de muro de 0,53 y de cubierta de 0,27 W/m$^2$K, y vidrio con U de 1,80 W/m$^2$K, SHGC de 0,35 y VT de 0,65. Son parámetros del paquete simulado; su evaluación constructiva y ambiental requiere productos y detalles definitivos.
'''
(R/'insumos/revision-envolvente.tex').write_text(text,encoding='utf-8')
