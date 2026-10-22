import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
m=json.loads((root/'modular/manifest.json').read_text()); ids=['walc','potter_engineering','mechanical_engineering','electrical_engineering','knoy_hall']; report={}
for a in m['assets']:
 if a['id'] not in ids: continue
 bpy.ops.wm.open_mainfile(filepath=str(root/'modular'/a['file']))
 bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get(); rows=[]
 for o in bpy.data.collections[a['collection']].all_objects:
  if o.type!='MESH': continue
  ev=o.evaluated_get(dg); ps=[ev.matrix_world@Vector(v) for v in ev.bound_box]
  rows.append(dict(name=o.name,parent=o.parent.name if o.parent else None,bounds=[[round(min(p[i] for p in ps),3),round(max(p[i] for p in ps),3)] for i in range(3)]))
 report[a['id']]={'placement':a['placement_origin_xy_m'],'objects':rows}
(root/'audit/walc_east/inspection.json').write_text(json.dumps(report,indent=2))
