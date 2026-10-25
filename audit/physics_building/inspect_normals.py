import bpy,collections
from mathutils import Vector
obj=bpy.data.objects['PHYS | recessed dark sash glazing']; m=obj.data
cnt=collections.Counter(tuple(round(x,1) for x in p.normal) for p in m.polygons)
print(cnt.most_common(12))
for d in [Vector((-.634,.773,0)),Vector((.634,-.773,0))]:
 faces=[p for p in m.polygons if p.normal.dot(d)>.8]
 print('faces dir',len(faces),'centers unique',len(set(tuple(round(sum(m.vertices[i].co[j] for i in p.vertices)/4,2) for j in range(3)) for p in faces)))
