import bpy,json,math
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend')
out=[]
for o in bpy.data.objects:
 if o.type=='MESH' and (o.name.startswith('KNOY_Illustrative_Door_') or o.name.startswith('KNOY_Ground_TracePartition_')):
  b=[o.matrix_world@Vector(c) for c in o.bound_box]
  mi=[min(v[i] for v in b) for i in range(3)];ma=[max(v[i] for v in b) for i in range(3)]
  if o.name.startswith('KNOY_Illustrative_Door_'):
   out.append({'name':o.name,'loc':list(o.location),'rot_z':o.rotation_euler.z,'dims':list(o.dimensions),'bounds': [mi,ma]})
print(json.dumps(out,indent=2))
