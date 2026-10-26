import bpy,json,collections
from mathutils import Vector
patterns=collections.Counter()
for o in bpy.data.objects:
 if o.type=='MESH':
  k=o.name.split('_')[:3]
  patterns['_'.join(k)]+=1
print('PREFIX_GROUPS',json.dumps(patterns.most_common(60)))
for n in ['Tark_NW_Wing_Brick_Shaft','Tark_SW_Wing_GF_Wall_N','Tark_SW_Wing_GF_Wall_S','Tark_SW_Wing_GF_Wall_E','Tark_SW_Wing_GF_Wall_W','Tark_Commons_Hub_Upper_Brick_Shaft','Tark_North_Entrance_Pavilion_Brick_Shaft','Tark_South_Entrance_Pavilion_Upper_Brick_Shaft']:
 o=bpy.data.objects.get(n)
 if o:
  pts=[o.matrix_world@Vector(v) for v in o.bound_box]
  print('OBJECT',n,'loc',list(o.location),'rot',list(o.rotation_euler),'dim',list(o.dimensions),'bounds',[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)],'mats',[m.name if m else None for m in o.data.materials])
for o in bpy.data.objects:
 if o.type=='MESH' and not o.data.materials: print('NOMAT',o.name)
