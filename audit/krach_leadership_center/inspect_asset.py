import bpy, json, math
from mathutils import Vector
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\krach_leadership_center.blend'
bpy.ops.wm.open_mainfile(filepath=p)
rows=[]
for o in bpy.data.objects:
 if o.type=='MESH':
  deps=bpy.context.evaluated_depsgraph_get(); ev=o.evaluated_get(deps); me=ev.to_mesh()
  pts=[o.matrix_world @ v.co for v in me.vertices]
  if pts:
   lo=[min(p[i] for p in pts) for i in range(3)]; hi=[max(p[i] for p in pts) for i in range(3)]
  else: lo=hi=[]
  ev.to_mesh_clear()
 else: lo=hi=[]
 rows.append({'name':o.name,'type':o.type,'loc':list(o.location),'dims':list(o.dimensions),'bounds':[lo,hi],'mats':[m.name for m in o.data.materials] if getattr(o.data,'materials',None) else [],'parent':o.parent.name if o.parent else None,'collections':[c.name for c in o.users_collection]})
print(json.dumps({'filepath':bpy.data.filepath,'collections':[c.name for c in bpy.data.collections],'scene_objects':len(bpy.data.objects),'objects':rows},indent=2))
