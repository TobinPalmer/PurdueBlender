import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
s=bpy.context.scene;c=s.camera
for col in s.collection.children:
 print('COL',col.name)
 for o in col.all_objects:
  if o.type!='MESH' or not len(o.data.vertices):continue
  pts=[o.matrix_world@v.co for v in o.data.vertices]
  lo=[min(v[i] for v in pts) for i in range(3)];hi=[max(v[i] for v in pts) for i in range(3)]
  sc=[world_to_camera_view(s,c,Vector((x,y,z))) for x in (lo[0],hi[0]) for y in (lo[1],hi[1]) for z in (lo[2],hi[2])]
  sx=[v.x for v in sc];sy=[v.y for v in sc]
  if max(sx)>.0 and min(sx)<1 and max(sy)>.0 and min(sy)<1:
   print(' ',o.name,'world',tuple(round(v,1) for v in lo),tuple(round(v,1) for v in hi),'screen',round(min(sx),2),round(max(sx),2),round(min(sy),2),round(max(sy),2))
