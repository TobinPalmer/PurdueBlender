import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap'); out={}
manifest=json.loads((P/'modular/manifest.json').read_text())
for a in manifest['assets']:
 if a['id'] not in ['class_of_1950','math_sciences','felix_haas_hall','stanley_coulter_hall']:continue
 bpy.ops.wm.open_mainfile(filepath=str(P/'modular'/a['file'])); bpy.context.view_layer.update()
 rows=[]
 for o in bpy.data.collections[a['collection']].all_objects:
  if o.type=='MESH' and any(t in o.name.lower() for t in ['wall','masonry','spandrel','brick','tower','root','ground_curtain']):
   pts=[list(o.matrix_world@Vector(c)) for c in o.bound_box]
   rows.append({'name':o.name,'parent':o.parent.name if o.parent else None,'location':list(o.location),'world':list(o.matrix_world.translation),'bounds':[[min(p[i] for p in pts)+ (a['placement_origin_xy_m'][i] if i<2 else 0),max(p[i] for p in pts)+(a['placement_origin_xy_m'][i] if i<2 else 0)] for i in range(3)]})
 out[a['id']]={'origin':a['placement_origin_xy_m'],'rows':rows,'empties':[{'name':o.name,'loc':list(o.location),'world':list(o.matrix_world.translation),'parent':o.parent.name if o.parent else None} for o in bpy.data.collections[a['collection']].all_objects if o.type=='EMPTY']}
(P/'audit/walc_south/inspect.json').write_text(json.dumps(out,indent=2))
