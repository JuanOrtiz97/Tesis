"""Run the installed EnergyPlus 9.4 C API in an isolated working directory.
API signature verified against NREL/EnergyPlus v9.4.0 runtime.py and state.py.
"""
from pathlib import Path
import ctypes,os,sys,shutil,re,json
W=Path('C:\\Users\\juand\\Documents\\New project 3\\Tesis-limpia\\output')
runtime=Path(r'C:\Users\juand\AppData\Local\DesignBuilder\EnergyPlus')
case=sys.argv[1];power=sys.argv[2]; warmup=int(sys.argv[3]) if len(sys.argv)>3 else 100
src=W/({'CB':'caso-base-revision-2026-09-12/corrida-09-cargas-estabilidad','C3':'C3-revision02/corrida-02'}[case])
dest=W/'sensibilidad-datacenter'/(f'{case}-{power}' + (f'-warmup{warmup}' if warmup!=100 else '') + ('-'+sys.argv[4] if len(sys.argv)>4 else ''));dest.mkdir(parents=True,exist_ok=True)
if (dest/'in.idf').exists():raise FileExistsError('Use a new suffix to preserve the existing run: '+str(dest))
s=(src/'in.idf').read_text(encoding='utf-8-sig')
if power!='control':
 matches=[]
 def change(m):
  block=m.group();a=[x.strip() for x in re.sub(r'!.*','',block).strip().rstrip(';').split(',')]
  if len(a)>7 and ':1PAXDC' in a[3].upper():
   assert a[5].lower()=='watts/area',(a[:9]);assert float(a[7])==500
   a[7]=power;matches.append(a[1]);return ',\n'.join(a)+';'
  return block
 s=re.sub(r'(?im)^\s*OtherEquipment\s*,[^;]*;',change,s)
 assert len(matches)==1,matches
else:matches=[]
if warmup!=100:
 def warm(m):
  a=[x.strip()for x in re.sub(r'!.*','',m.group()).strip().rstrip(';').split(',')];assert a[7]=='100';a[7]=str(warmup);return ',\n'.join(a)+';'
 s,n=re.subn(r'(?im)^Building\s*,[^;]*;',warm,s);assert n==1
(dest/'in.idf').write_text(s,encoding='utf-8')
shutil.copy2(W/'C3-revision02/corrida-02/in.epw',dest/'in.epw')
shutil.copy2(runtime/'Energy+.idd',dest/'Energy+.idd')
(dest/'provenance.json').write_text(json.dumps({'source':str(src),'changed_equipment':matches,'watts_per_m2':power,'max_warmup_days':warmup,'api':'EnergyPlus 9.4 installed with DesignBuilder'},indent=2))
os.chdir(dest);handle=os.add_dll_directory(str(runtime));dll=ctypes.CDLL(str(runtime/'energyplusapi.dll'))
dll.stateNew.argtypes=[];dll.stateNew.restype=ctypes.c_void_p
state=dll.stateNew()
args=[b'energyplus',b'-i',b'Energy+.idd',b'-w',b'in.epw',b'-d',b'.',b'in.idf'];argtype=ctypes.c_char_p*len(args)
dll.energyplus.argtypes=[ctypes.c_void_p,ctypes.c_int,argtype];dll.energyplus.restype=ctypes.c_int
code=dll.energyplus(state,len(args),argtype(*args));print('EXIT_CODE',code,flush=True)
dll.stateDelete.argtypes=[ctypes.c_void_p];dll.stateDelete.restype=None;dll.stateDelete(state)
sys.exit(code)
