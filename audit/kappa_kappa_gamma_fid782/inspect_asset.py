import bpy,json
from mathutils import Vector
for o in bpy.context.scene.objects:
 v=[o.matrix_world @ Vector(c) for c in o.bound_box]
 lo=[min(p[i] for p in v) for i in range(3)]; hi=[max(p[i] for p in v) for i in range(3)]
 print(json.dumps({'name':o.name,'type':o.type,'vertices':len(o.data.vertices) if o.type=='MESH' else 0,'faces':len(o.data.polygons) if o.type=='MESH' else 0,'bounds':{'min':lo,'max':hi},'materials':[m.name for m in o.data.materials] if o.type=='MESH' else []}))
