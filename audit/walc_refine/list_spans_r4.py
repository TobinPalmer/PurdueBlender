import bpy
from mathutils import Vector
for o in bpy.data.collections['Asset_walc'].all_objects:
 if o.type!='MESH' or not o.name.startswith('WALC_Source906_Edge_') or not any(o.name.endswith(f'_Band{k}') for k in (2,4,6)): continue
 ps=[o.matrix_world@v.co for v in o.data.vertices]
 xs=[p.x for p in ps]; ys=[p.y for p in ps]
 dx=max(xs)-min(xs); dy=max(ys)-min(ys); length=max(dx,dy)
 if length>4: print(o.name,round(length,2),round((max(xs)+min(xs))/2,2),round((max(ys)+min(ys))/2,2))
