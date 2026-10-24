import bpy
from mathutils import Vector
for ob in sorted([o for o in bpy.context.scene.objects if o.type=='MESH'],key=lambda o:o.dimensions.length,reverse=True)[:30]:
 mats=[m.name if m else 'None' for m in ob.data.materials]
 print('OBJ',ob.name,'dims',tuple(round(x,1) for x in ob.dimensions),'materials',mats)
