import bpy,collections
from mathutils import Vector
m=bpy.data.objects['PHYS | recessed dark sash glazing'].data
c=collections.Counter(round(p.normal.dot(Vector((sum(m.vertices[i].co.x for i in p.vertices)/4,sum(m.vertices[i].co.y for i in p.vertices)/4,0)).normalized()),1) for p in m.polygons)
print(c)
