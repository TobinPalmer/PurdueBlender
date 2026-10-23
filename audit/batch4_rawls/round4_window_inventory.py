import bpy
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend')
for o in bpy.data.objects:
 if any(k in o.name.lower() for k in ['window','glass','glazing','curtain']):
  bb=[o.matrix_world@__import__('mathutils').Vector(c) for c in o.bound_box] if o.type=='MESH' else []
  if bb:print(o.name,'loc',tuple(o.location),'bounds',[(round(min(v[i] for v in bb),2),round(max(v[i] for v in bb),2)) for i in range(3)],'mat',[m.name for m in o.data.materials])
