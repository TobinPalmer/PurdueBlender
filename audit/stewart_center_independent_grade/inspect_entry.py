import bpy, json
from mathutils import Vector
c=bpy.data.collections['Asset_stewart_center']
for o in sorted([o for o in c.all_objects if o.name.startswith('STEW_Portico_') or o.name.startswith('STEW_South_')],key=lambda o:o.name):
 if o.type!='MESH': continue
 vs=[o.matrix_world@Vector(v) for v in o.bound_box]
 print(o.name,[[round(min(v[i] for v in vs),2),round(max(v[i] for v in vs),2)] for i in range(3)],[m.name if m else None for m in o.data.materials])
