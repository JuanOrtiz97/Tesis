from pathlib import Path
import re,csv,json
import pandas as pd
R=Path(r'C:\Users\juand\Desktop\Tesis de Maestria - Juan Ortiz\01_Documento_tesis\Repositorios\Trabajo_completo\Tesis-limpia')
W=Path(r'C:\Users\juand\Documents\New project 3\Tesis-limpia\output')
sources={'CB':W/'caso-base-revision-2026-09-12/corrida-09-cargas-estabilidad','C1':W/'C1-estrategias-pasivas/corrida-01','C2':W/'C2-materiales/corrida-01','C3 r01':W/'C3-combinado/corrida-01','C3 r02':W/'C3-revision02/corrida-02'}
results=[];metadata={}
for case,folder in sources.items():
 selected={};values={};env=[]
 with (folder/'eplusout.eso').open() as f:
  for line in f:
   if 'End of Data Dictionary' in line:break
   if '!RunPeriod' not in line:continue
   p=line.split('!')[0].strip().split(',');var=p[-1].strip()
   if var in ['Zone Ideal Loads Supply Air Total Cooling Rate [W]','Zone Ideal Loads Supply Air Sensible Cooling Rate [W]','Zone Air System Sensible Cooling Rate [W]','InteriorLights:Electricity [J]','InteriorEquipment:Electricity [J]']:
    selected[p[0]]=(p[2].strip() if len(p)>3 else 'Facility',var)
  for line in f:
   p=line.strip().split(',')
   if p[0]=='1':env.append(p[1])
   if p[0] in selected:values[p[0]]=float(p[1])
 assert len(env)==1,(case,env)
 sums={};totalzone={}
 for k,v in values.items():
  zone,var=selected[k];q=v*(8.76 if '[W]' in var else 1/3600000)
  sums[var]=sums.get(var,0)+q
  if var=='Zone Ideal Loads Supply Air Total Cooling Rate [W]':totalzone[zone.replace(' IDEAL LOADS AIR','')]=q
 dc=sum(q for z,q in totalzone.items() if z.endswith(':1PAXDC'))
 total=sum(totalzone.values());row={'caso':case,'enfriamiento_kWh':total,'datacenter_kWh':dc,'sin_datacenter_kWh':total-dc,'equipos_kWh':sums['InteriorEquipment:Electricity [J]'],'iluminacion_kWh':sums['InteriorLights:Electricity [J]']}
 settings=folder/'simplehvacsettings.dat'
 if not settings.exists() and case=='CB':settings=sources['C1']/'simplehvacsettings.dat'
 if settings.exists():
  cop={}
  for line in settings.read_text().splitlines():
   p=[x.strip() for x in line.split('#')[1:]]
   if p and p[0] in totalzone:cop[p[0]]=float(p[3])
  row['electricidad_enfriamiento_estimacion_kWh']=sum(q/cop[z] for z,q in totalzone.items()) if all(z in cop and cop[z]>0 for z in totalzone) else None
 results.append(row);metadata[case]=sums
df=pd.DataFrame(results)
df['ahorro_total_pct']=100*(1-df.enfriamiento_kWh/df.enfriamiento_kWh.iloc[0]);df['ahorro_sin_dc_pct']=100*(1-df.sin_datacenter_kWh/df.sin_datacenter_kWh.iloc[0])

idf=(R/'datos/db-caso-base-revision09.idf').read_text(encoding='utf-8-sig')
objects=[[x.strip() for x in o.split(',')] for o in re.sub(r'!.*','',idf).split(';')]
area=sum(float(p[10]) for p in objects if p[0].upper()=='ZONE' and 'ATRIO' not in p[1])
df['electricidad_total_estimacion_kWh']=df.electricidad_enfriamiento_estimacion_kWh+df.equipos_kWh+df.iluminacion_kWh
df['area_referencia_m2']=area
df['EUI_estimado_kWh_m2_anio']=df.electricidad_total_estimacion_kWh/area
df.to_csv(R/'datos/revision-comparacion-datacenter.csv',index=False)
(W/'revision-datos-validacion.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
print(df.round(3).to_string(index=False));print('CB sensible',metadata['CB'])
