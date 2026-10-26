import bpy,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; ASSET=ROOT/'modular'/'buildings'/'massing_chi_omega_a9eb08d.blend'; SRC=ROOT/'audit'/'chi_omega'/'sources'/'purdue_gis_fid781_chi_omega_2026-10-26.json'
bpy.ops.wm.open_mainfile(filepath=str(ASSET));o=bpy.data.objects['Chi Omega']; d=json.load(open(SRC))['features'][0]; ring=d['geometry']['rings'][0][:-1]; E=set(); A=set();
for lon,lat in ring:E.add((round((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),4),round((lat-40.4274)*111040,4)))
for v in o.data.vertices:
 if abs(v.co.z)<1e-6:A.add((round(v.co.x,4),round(v.co.y,4)))
print('expected',sorted(E));print('actual',sorted(A));print('diff e-a',E-A,'a-e',A-E)
