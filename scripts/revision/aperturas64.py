from pathlib import Path
import re,numpy as np,pandas as pd
R=Path(r'C:\Users\juand\Desktop\Tesis de Maestria - Juan Ortiz\01_Documento_tesis\Repositorios\Trabajo_completo\Tesis-limpia');W=Path('C:\\Users\\juand\\Documents\\New project 3\\Tesis-limpia\\output')
sources={'CB':'caso-base-revision-2026-09-12/corrida-09-cargas-estabilidad','C1':'C1-estrategias-pasivas/corrida-01','C2':'C2-materiales/corrida-01','C3 r01':'C3-combinado/corrida-01','C3 r02':'C3-revision02/corrida-02'}
rows=[];assumptions=[]
for case,folder in sources.items():
 p=W/folder/'in.idf';a=[[x.strip()for x in t.split(',')]for t in re.sub(r'!.*','',p.read_text(encoding='utf-8-sig')).split(';')]
 def index(kind):return{x[1]:x for x in a if x[0].lower()==kind.lower()}
 zones=index('Zone');sur=index('BuildingSurface:Detailed');afn=index('AirflowNetwork:MultiZone:Surface');com=index('AirflowNetwork:MultiZone:Component:DetailedOpening')
 for z,zone in zones.items():
  if 'XOFX'not in z:continue
  total=0;cap=0;n=0
  for x in index('FenestrationSurface:Detailed').values():
   par=sur[x[4]]
   if x[2]!='Window' or par[4]!=z or par[5]!='Outdoors':continue
   v=np.array(list(map(float,x[10:]))).reshape(-1,3);ar=np.linalg.norm(np.cross(v,np.roll(v,-1,axis=0)).sum(axis=0)/2)*float(x[8]or 1);total+=ar
   if x[1] in afn and afn[x[1]][2] in com:
    c=com[afn[x[1]][2]];factor=max(float(c[9+5*i])*float(c[10+5*i])for i in range(int(c[6])))
    cap+=ar*factor;n+=1
  rows.append({'caso':case,'zona':z.split(':')[-1].replace('X','-'),'piso_m2':float(zone[10]),'ventana_exterior_m2':total,'apertura_max_modelo_m2':cap,'apertura_max_piso_pct':100*cap/float(zone[10]),'ventanas_AFN':n})
 for x in index('People').values():
  if 'XOFX' in x[2]:assumptions.append({'caso':case,'zona':x[2],'campos_people':' | '.join(x[3:])})
df=pd.DataFrame(rows);df.to_csv(R/'datos/revision-aperturas-cinco-casos.csv',index=False)
pd.DataFrame(assumptions).to_csv(R/'datos/revision-supuestos-people.csv',index=False)
print(df[df.caso=='C3 r02'].round(3).to_string(index=False))
