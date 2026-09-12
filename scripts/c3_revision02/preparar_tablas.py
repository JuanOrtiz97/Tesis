from pathlib import Path
import csv, json, hashlib, re
import numpy as np
import pandas as pd

ROOT=Path('C:/Users/juand/Documents/New project 3/Tesis-limpia/output/C3-revision02')
OUT=ROOT/'tablas-y-graficos';OUT.mkdir(exist_ok=True)
VARS={'Zone Operative Temperature [C]':'temperatura_operativa_C',
      'InteriorLights:Electricity [J]':'iluminacion_J',
      'Zone Ideal Loads Supply Air Total Cooling Rate [W]':'enfriamiento_total_W',
      'Zone Ideal Loads Supply Air Sensible Cooling Rate [W]':'enfriamiento_sensible_W'}
sources={'CB':ROOT.parent/'caso-base-revision-2026-09-12/corrida-09-cargas-estabilidad/eplusout.eso','C3':ROOT/'corrida-02/eplusout.eso'}
frames=[];checks={}
for case,path in sources.items():
    dictionary={};selected={};series={};monthly=[];envs=[];env='';month=0
    with path.open(errors='strict') as f:
        for line in f:
            if 'End of Data Dictionary' in line:break
            fields=line.strip().split(',')
            if not fields[0].isdigit() or int(fields[0])<=6:continue
            before,_,freq=line.strip().partition('!');parts=before.rstrip().split(',')
            dictionary[fields[0]]={'key':parts[2] if len(parts)>3 else 'Facility','variable':parts[3].strip() if len(parts)>3 else parts[2].strip(),'frequency':freq.split()[0] if freq else ''}
            meta=dictionary[fields[0]]
            if meta['frequency'].startswith('Hourly') and meta['variable'] in VARS:
                selected[fields[0]]=meta;series[fields[0]]=[]
        for line in f:
            p=line.strip().split(',');rid=p[0]
            if rid=='1':env=p[1];envs.append(env)
            elif rid=='4':month=int(p[2])
            elif rid in selected:series[rid].append(float(p[1]))
            if case=='C3' and rid in dictionary and dictionary[rid]['frequency'].startswith(('Monthly','RunPeriod')):
                m=dictionary[rid];monthly.append([rid,env,m['key'],m['variable'],m['frequency'],month if m['frequency'].startswith('Monthly') else '',p[1],'|'.join(p[2:])])
    assert len(envs)==1,envs
    assert all(len(v)==8760 for v in series.values()),{k:len(v) for k,v in series.items()}
    dates=pd.date_range('2025-01-01',periods=8760,freq='h')
    cols={f"{m['key'].replace(' IDEAL LOADS AIR','')}|{VARS[m['variable']]}":series[rid] for rid,m in selected.items()}
    wide=pd.DataFrame(cols,index=dates);wide.index.name='inicio_intervalo_horario_local'
    wide.to_csv(OUT/f'{case}-series-horarias.csv.gz',compression='gzip',float_format='%.10g')
    rows=[]
    for col in wide:
        zone,var=col.split('|');v=wide[col]
        for mo,g in v.groupby(v.index.month):
            rows.append({'caso':case,'zona':zone,'mes':mo,'variable':var.replace('_W','_kWh_termicos').replace('_J','_kWh_electricos'),'valor':g.sum()/1000 if var.endswith('_W') else g.sum()/3600000 if var.endswith('_J') else g.mean(),'horas':len(g)})
    frames.extend(rows)
    checks[case]={'source':str(path.resolve()),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'ambiente':envs,'series':len(series),'horas_por_serie':8760}
    if case=='C3':
        annual_report=sum(float(x[6])*8760/1000 for x in monthly if x[4].startswith('RunPeriod') and x[3]=='Zone Ideal Loads Supply Air Total Cooling Rate [W]')
        annual_hourly=sum(sum(series[rid])/1000 for rid,meta in selected.items() if meta['variable']=='Zone Ideal Loads Supply Air Total Cooling Rate [W]')
        assert abs(annual_report-annual_hourly)<.01,(annual_report,annual_hourly)
        checks[case]['contraste_anual_kWh_termicos']={'reporte':annual_report,'integracion_horaria':annual_hourly,'diferencia':annual_report-annual_hourly}
        with (OUT/'C3-todas-variables-mensuales-anuales.csv').open('w',encoding='utf-8-sig',newline='') as o:
            w=csv.writer(o);w.writerow(['id_eso','ambiente','objeto','variable_unidad_original','frecuencia','mes','valor_original','estadisticos_adicionales_orden_eso']);w.writerows(monthly)
        (OUT/'diccionario-ESO-C3.json').write_text(json.dumps(dictionary,ensure_ascii=False,indent=2),encoding='utf-8')
df=pd.DataFrame(frames);df.to_csv(OUT/'CB-C3-mensual-por-zona.csv',index=False,encoding='utf-8-sig')
cool=df[df.variable=='enfriamiento_total_kWh_termicos'].pivot(index=['zona','mes'],columns='caso',values='valor').reset_index()
cool['diferencia_kWh']=cool.C3-cool.CB;cool['variacion_pct']=np.where(cool.CB>1e-6,100*cool.diferencia_kWh/cool.CB,np.nan)
cool.to_csv(OUT/'comparacion-enfriamiento-mensual.csv',index=False,encoding='utf-8-sig')
annual=cool.groupby('zona')[['CB','C3']].sum();annual['diferencia_kWh']=annual.C3-annual.CB;annual['variacion_pct']=np.where(annual.CB>1e-6,100*annual.diferencia_kWh/annual.CB,np.nan)
annual.to_csv(OUT/'comparacion-enfriamiento-anual.csv',encoding='utf-8-sig')
checks['totales_enfriamiento_kWh_termicos']=annual[['CB','C3']].sum().to_dict()
checks['CB_contraste_eso_previo']=abs(checks['totales_enfriamiento_kWh_termicos']['CB']-84759.410853)<.01
assert checks['CB_contraste_eso_previo']
checks['estado']='Comparación preliminar; pendientes del CB y evaluación de confort e iluminación.'
(OUT/'validacion-datos.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(checks['totales_enfriamiento_kWh_termicos']))
