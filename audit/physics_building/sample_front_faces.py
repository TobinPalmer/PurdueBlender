import bpy
from mathutils import Vector
obj=bpy.data.objects['PHYS | recessed dark sash glazing']; m=obj.data
D=Vector((-.634,.773,0)).normalized()
for p in m.polygons:
 if p.normal.dot(D)>.99:
  cen=sum((m.vertices[i].co for i in p.vertices),Vector())/4
  print(tuple(round(v,2) for v in cen), tuple(round(v,1) for v in p.normal));
  if cen.z>5: break
