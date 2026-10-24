import bpy,json
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\morgan_j_burke_boilermaker_aquatic_center.blend')
c=bpy.data.objects['AQUA R3 | subtle standing seams on estimated roof'].data
rows=[]
for i,s in enumerate(c.splines):rows.append({'i':i,'pts':[list(p.co) for p in s.points]})
Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\batchC_boilermaker_aquatic_r1\seams_inspect.json').write_text(json.dumps(rows))
