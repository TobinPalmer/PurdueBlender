import bpy,json
from pathlib import Path
from mathutils import Vector
p=r'modular/buildings/massing_purdue_police_department_19f467e.blend'
bpy.ops.wm.open_mainfile(filepath=p)
result={'scene':bpy.context.scene.name,'collections':[],'objects':[]}
for c in bpy.data.collections:
 if c.users>0: result['collections'].append({'name':c.name,'objects':[o.name for o in c.objects]})
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  pts=[o.matrix_world@Vector(c) for c in o.bound_box]
  bounds=[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)]
  result['objects'].append({'name':o.name,'verts':len(o.data.vertices),'faces':len(o.data.polygons),'bounds':bounds,'location':list(o.location),'rotation':list(o.rotation_euler),'scale':list(o.scale)})
Path('audit/massing_purdue_police_department_19f467e/starting_asset_inspection.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
