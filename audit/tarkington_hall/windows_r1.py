import bpy
from mathutils import Vector
for prefix in ['Tark_Win_East','Tark_Win_West','Tark_Win_North','Tark_Win_South','Tark_Sill_East','Tark_Sill_West','Tark_Sill_North','Tark_Sill_South']:
 arr=sorted([o for o in bpy.data.objects if o.name.startswith(prefix)],key=lambda o:o.name)
 print('\n',prefix,len(arr))
 for o in arr[:5]+arr[-5:]:
  q=o.matrix_world.translation
  print(o.name,'center',tuple(round(v,2) for v in q),'dim',tuple(round(v,2) for v in o.dimensions))

