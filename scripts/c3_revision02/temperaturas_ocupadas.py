from pathlib import Path
import re,json
import pandas as pd
P=Path('C:/Users/juand/Documents/New project 3/Tesis-limpia/output/C3-revision02')
R=Path('C:/Users/juand/Desktop/Tesis de Maestria - Juan Ortiz/01_Documento_tesis/Repositorios/Trabajo_completo/Tesis-limpia')
def objects(path):
    return [[v.strip() for v in b.split(',')] for b in re.sub(r'!.*','',path.read_text()).split(';') if b.strip()]
records=[]
for case,folder in [('CB',P.parent/'caso-base-revision-2026-09-12/corrida-09-cargas-estabilidad'),('C3',P/'corrida-02')]:
    obj=objects(folder/'in.idf')
    rows=lambda typ:[x for x in obj if x[0].lower()==typ.lower()]
    people=[x for x in rows('People') if 'OFX' in x[2]]
    assert len(people)==6 and all(x[3]=='8:00 - 18:00 Mon - Sat' for x in people)
    weeks=[x for x in rows('Schedule:Week:Daily') if x[1].startswith('8:00 - 18:00 Mon - Sat_')]
    assert len(weeks)==12 and all(x[2:9]==['11']+['1']*6 for x in weeks)
    day=next(x for x in rows('Schedule:Day:List') if x[1]=='1')
    assert day[4]=='60' and list(map(float,day[5:]))==[0]*8+[1]*10+[0]*6
    assert next(x for x in rows('Schedule:Day:Interval') if x[1]=='11')[4:]==['24:00','0']
    assert not rows('RunPeriodControl:SpecialDays') and not rows('RunPeriodControl:DaylightSavingTime')
    if (folder/'in.epw').exists():
        assert 'HOLIDAYS/DAYLIGHT SAVINGS,No,0,0,0' in (folder/'in.epw').read_text()
    rp=rows('RunPeriod')[0];assert rp[2:8]==['1','1','2025','12','31','2025'] and rp[9]=='No'
    data=pd.read_csv(P/f'tablas-y-graficos/{case}-series-horarias.csv.gz',index_col=0,parse_dates=True)
    mask=(data.index.dayofweek<6)&(data.index.hour>=8)&(data.index.hour<18)
    assert mask.sum()==3130
    for person in sorted(people,key=lambda x:x[2]):
        zone=person[2];v=data.loc[mask,zone+'|temperatura_operativa_C']
        assert len(v)==3130 and v.notna().all()
        records.append({'caso':'C3 r02' if case=='C3' else case,'zona':zone,'horas_ocupadas':len(v),'media_C':v.mean(),'mediana_C':v.median(),'percentil95_C':v.quantile(.95),'maximo_C':v.max()})
d=pd.DataFrame(records);d.to_csv(R/'datos/C3r02-temperatura-oficinas-ocupadas.csv',index=False,encoding='utf-8-sig')
table=d.pivot(index='zona',columns='caso',values=['media_C','percentil95_C'])
table['delta_media']=table[('media_C','C3 r02')]-table[('media_C','CB')]
print(table.to_string())
s=r'''\clearpage
\subsection{Respuesta térmica durante la ocupación de oficinas}
La temperatura operativa se compara en las seis oficinas intervenidas mediante 3.130 intervalos horarios ocupados por zona: lunes a sábado, de 08:00 a 18:00, según el calendario 2025 del modelo, sin festivos adicionales. Se conservan los mismos horarios en ambas corridas. El percentil 95 describe la parte alta de la distribución; no es un umbral normativo de confort.
\begin{table}[H]\centering
\caption{Temperatura operativa en horas ocupadas: caso base y C3 revisión 02}
{\small\singlespacing\renewcommand{\arraystretch}{1.25}
\begin{tabular}{lrrrrr}\toprule
 & \multicolumn{2}{c}{Media (\textdegree C)} & \multicolumn{2}{c}{P95 (\textdegree C)} & \\
Oficina & CB & C3 r02 & CB & C3 r02 & $\Delta$ media (K) \\ \midrule
'''
fmt=lambda v:f'{v:.2f}'.replace('.',',')
for zone,row in table.iterrows():
    name=zone.split(':')[1].replace('X','-')
    s+=name+' & '+' & '.join(fmt(row[key]) for key in [('media_C','CB'),('media_C','C3 r02'),('percentil95_C','CB'),('percentil95_C','C3 r02'),('delta_media','')])+r' \\'+'\n'
s+=r'''\bottomrule\end{tabular}}
\fuente{Elaboración propia con series horarias de EnergyPlus y horarios de ocupación del modelo. $\Delta$ = C3 r02 $-$ CB.}
\end{table}
Estos estadísticos cuantifican la respuesta térmica, pero no acreditan C01. La evaluación de confort requiere separar las horas de funcionamiento mecánico y natural, aplicar el método correspondiente y comprobar sus condiciones de actividad, vestimenta, velocidad del aire y cobertura espacial. Una reducción de demanda o de temperatura media no equivale automáticamente a mayor porcentaje de horas confortables.
'''
(R/'insumos/c3-revision02-temperaturas.tex').write_text(s,encoding='utf-8')
