from pathlib import Path
import numpy as np,pandas as pd,json
R=Path(r'C:\Users\juand\Desktop\Tesis de Maestria - Juan Ortiz\01_Documento_tesis\Repositorios\Trabajo_completo\Tesis-limpia');W=Path('C:\\Users\\juand\\Documents\\New project 3\\Tesis-limpia\\output')
sources={'CB':'caso-base-revision-2026-09-12/corrida-09-cargas-estabilidad','C1':'C1-estrategias-pasivas/corrida-01','C2':'C2-materiales/corrida-01','C3 r01':'C3-combinado/corrida-01','C3 r02':'C3-revision02/corrida-02'}
dates=pd.date_range('2025-01-01',periods=8760,freq='h');mask=(dates.dayofweek<6)&(dates.hour>=8)&(dates.hour<18);assert mask.sum()==3130
records=[]
for case,folder in sources.items():
 selected={};series={};env=[]
 with (W/folder/'eplusout.eso').open() as f:
  for line in f:
   if 'End of Data Dictionary' in line:break
   if '!Hourly' not in line:continue
   p=line.split('!')[0].strip().split(',')
   if len(p)<4:continue
   key=p[2].strip();var=p[3].strip()
   if ('PBXOFX' in key or '1PAXOFX' in key) and var in ['Zone Thermal Comfort Fanger Model PMV []','Zone Thermal Comfort Fanger Model PPD [%]']:
    selected[p[0]]=(key,var);series[p[0]]=[]
  for line in f:
   p=line.strip().split(',')
   if p[0]=='1':env.append(p[1])
   if p[0] in series:series[p[0]].append(float(p[1]))
 assert len(env)==1 and len(selected)==12,(case,env,len(selected))
 by={}
 for k,v in series.items():
  assert len(v)==8760
  key,var=selected[k];by.setdefault(key,{})[var]=np.array(v)[mask]
 for key,v in by.items():
  pmv=v['Zone Thermal Comfort Fanger Model PMV []'];ppd=v['Zone Thermal Comfort Fanger Model PPD [%]'];assert np.isfinite(pmv).all() and (ppd>=0).all() and (ppd<=100).all()
  zone=key.replace('PEOPLE ','').split(':')[-1].replace('X','-')
  records.append({'caso':case,'zona':zone,'horas_analizadas':3130,'PMV_medio':pmv.mean(),'PPD_medio_pct':ppd.mean(),'horas_PMV_05':int((abs(pmv)<=.5).sum()),'porcentaje_PMV_05':(abs(pmv)<=.5).mean()*100,'horas_PMV_calor':int((pmv>.5).sum()),'horas_PMV_frio':int((pmv<-.5).sum())})
df=pd.DataFrame(records);df.to_csv(R/'datos/revision-confort-PMV-cinco-casos.csv',index=False);print(df.round(2).to_string(index=False))
