from pathlib import Path
import re,json,csv
from comparar_control64 import total
W=Path('C:\\Users\\juand\\Documents\\New project 3\\Tesis-limpia\\output')
R=Path(r'C:\Users\juand\Desktop\Tesis de Maestria - Juan Ortiz\01_Documento_tesis\Repositorios\Trabajo_completo\Tesis-limpia')
def canonical(p):return [[x.strip() for x in t.strip().split(',')]for t in re.sub(r'!.*','',p.read_text(encoding='utf-8-sig')).split(';') if t.strip()]
rows=[]
for power in ['150','300','control']:
 vals={}
 for case in ['CB','C3']:
  d=W/'sensibilidad-datacenter'/(f'{case}-{power}'+('-warmup500' if case=='C3' and power=='150' else ('-verificado' if case=='CB' and power=='300' else '')));end=(d/'eplusout.end').read_text();assert 'Completed Successfully' in end and '0 Severe Errors' in end,end
  orig=canonical(W/'sensibilidad-datacenter'/f'{case}-control'/'in.idf');new=canonical(d/'in.idf');assert len(orig)==len(new)
  diff=[(i,j,a,b)for i,(a1,b1) in enumerate(zip(orig,new))for j,(a,b)in enumerate(zip(a1,b1))if a!=b]
  if power!='control':assert any(x[1:]==(7,'500',power) for x in diff),diff
  if case=='C3' and power=='150':assert len(diff)==2 and any(x[1:]==(7,'100','500') for x in diff),diff
  elif power!='control':assert len(diff)==1,diff
  vals[case]=total(d)
  print(case,power,vals[case],end.strip())
 rows.append({'carga_dc_W_m2':500 if power=='control' else int(power),'CB_kWh_termicos':vals['CB'],'C3r02_kWh_termicos':vals['C3'],'ahorro_kWh':vals['CB']-vals['C3'],'ahorro_pct':100*(1-vals['C3']/vals['CB'])})
with (R/'datos/revision-sensibilidad-datacenter.csv').open('w',newline='',encoding='utf-8')as f:w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
print(json.dumps(rows,indent=2))
