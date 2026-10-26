import bpy
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath=str(Path(__file__).with_name('rawls_hall_r9_candidate.blend')))
for k in ['RAWL_2026_1086_Chair','RAWL_2026_1086_Desk']:
 objs=[o for o in bpy.data.objects if o.name.startswith(k)]
 print(k,'count',len(objs))
 print([(o.name,tuple(round(v,2) for v in o.location),tuple(round(v,2) for v in o.dimensions)) for o in objs[:5]])
