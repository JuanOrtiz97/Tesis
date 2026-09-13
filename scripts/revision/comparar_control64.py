from pathlib import Path
def total(folder):
 ids=set();val=0; count=0; complete=False
 with (Path(folder)/'eplusout.eso').open() as f:
  for l in f:
   if 'End of Data Dictionary' in l:break
   if '!RunPeriod' in l and 'Zone Ideal Loads Supply Air Total Cooling Rate [W]' in l:ids.add(l.split(',')[0])
  for l in f:
   if l.strip()=='End of Data':complete=True
   a=l.split(',')
   if a[0] in ids:val+=float(a[1])*8.76;count+=1
 assert complete and len(ids)==25 and count==25,(folder,complete,len(ids),count)
 return val
if __name__=='__main__':
 w=Path(r'C:\Users\juand\Documents\New project 3\Tesis-limpia\output')
 for case,src in [('CB','caso-base-revision-2026-09-12/corrida-09-cargas-estabilidad'),('C3','C3-revision02/corrida-02')]:
  dst=w/'sensibilidad-datacenter'/f'{case}-control'
  if not (dst/'eplusout.end').exists():continue
  old=total(w/src);new=total(dst);print(case,old,new,'delta',new-old);assert abs(new-old)<.001
