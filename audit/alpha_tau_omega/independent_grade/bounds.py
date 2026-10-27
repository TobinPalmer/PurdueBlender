import bpy,json
from pathlib import Path
asset=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\massing_house_301840870_c45a5f4.blend')
out=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\alpha_tau_omega\independent_grade\object_bounds.json')
bpy.ops.wm.open_mainfile(filepath=str(asset)); col=bpy.data.collections['Asset_massing_house_301840870_c45a5f4']
rows=[]
for o in sorted(col.objects,key=lambda x:x.name):
 if o.type!='MESH': continue
 cs=[o.matrix_world@v.co for v in o.data.vertices]
 if not cs: continue
 b=[[min(c[i] for c in cs),max(c[i] for c in cs)] for i in range(3)]
 if any(k in o.name.lower() for k in ('mass','wing','wall','block','tower','addition','connector','house','kitchen')):
  rows.append({'name':o.name,'bounds':b,'verts':len(o.data.vertices),'polygons':len(o.data.polygons)})
out.write_text(json.dumps(rows,indent=2)); print(json.dumps(rows,indent=2))
