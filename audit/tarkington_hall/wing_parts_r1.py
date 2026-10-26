import bpy,json
from mathutils import Vector
for code in ['NW','SW','NE','SE']:
 arr=[o for o in bpy.data.objects if o.name.startswith(f'Tark_{code}_Wing_')]
 print(code,'count',len(arr))
 for o in arr:
  pts=[o.matrix_world@Vector(v) for v in o.bound_box]
  b=[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)]
  print(' ',o.name,[round(x,2) for x in o.dimensions],[[round(x,2) for x in a] for a in b])
for prefix in ['Tark_Roof_Penthouse','Tark_Roof_HVAC']:
 for o in sorted([o for o in bpy.data.objects if o.name.startswith(prefix)],key=lambda o:o.name):
  print('ROOF_DETAIL',o.name,tuple(round(v,2) for v in o.matrix_world.translation),tuple(round(v,2) for v in o.dimensions))
for o in bpy.data.objects:
 if o.name.startswith('Tark_East_Courtyard_Connector'):
  pts=[o.matrix_world@Vector(v) for v in o.bound_box]
  b=[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)]
  print('CONNECTOR',o.name,[[round(x,2) for x in a] for a in b])
