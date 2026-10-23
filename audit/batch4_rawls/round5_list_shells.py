import bpy,os
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'))
for o in bpy.data.objects:
 if any(k in o.name.lower() for k in ['floor','slab','roof','masonry','shell','door','stair','atrium']):
  if o.type=='MESH':
   bb=[o.matrix_world@__import__('mathutils').Vector(c) for c in o.bound_box]
   print(o.name,[(round(min(v[i] for v in bb),2),round(max(v[i] for v in bb),2)) for i in range(3)])
