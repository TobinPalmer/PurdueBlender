import bpy,json
from pathlib import Path
p=Path(r'modular/buildings/massing_life_science_ranges_greenhouse_and_service_building_c96231f.blend').resolve()
bpy.ops.wm.open_mainfile(filepath=str(p))
for o in bpy.data.objects:
 print(o.name,o.type,'loc',list(o.location),'dims',list(o.dimensions),'verts',len(o.data.vertices) if o.type=='MESH' else None,'polys',len(o.data.polygons) if o.type=='MESH' else None,'mats',[m.name for m in o.data.materials] if o.type=='MESH' else None)
 if o.type=='MESH':
  from mathutils import Vector
  pts=[o.matrix_world@Vector(v.co) for v in o.data.vertices]
  print('bounds',[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)])
