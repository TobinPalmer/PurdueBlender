import bpy, json, math
from mathutils import Vector
for obj in bpy.context.scene.objects:
 if obj.type!='MESH': continue
 pts=[obj.matrix_world @ v.co for v in obj.data.vertices]
 print('OBJECT',obj.name,'verts',len(pts),'faces',len(obj.data.polygons))
 print('bounds',[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)])
 print('first', [tuple(round(x,3) for x in (obj.matrix_world@v.co)) for v in obj.data.vertices[:20]])
