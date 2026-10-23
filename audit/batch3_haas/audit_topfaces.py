import bpy
from mathutils import Vector
for o in bpy.data.objects:
 if o.type!='MESH' or not o.name.startswith('HAAS'):continue
 big=[]
 for p in o.data.polygons:
  wno=o.matrix_world.to_3x3()@p.normal
  co=[o.matrix_world@o.data.vertices[i].co for i in p.vertices]
  if wno.z>.98 and p.area>5:big.append((round(p.area,1),round(max(v.z for v in co),2),len(p.vertices)))
 if big:print(o.name,'top',big[:8])
