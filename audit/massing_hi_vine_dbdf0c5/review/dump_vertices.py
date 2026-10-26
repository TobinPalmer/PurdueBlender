import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/massing_hi_vine_dbdf0c5.blend')
o=bpy.data.objects['Hi Vine']; v=o.data.vertices
for i,x in enumerate(v):
 if abs((o.matrix_world@x.co).z)<1e-5: print(i,tuple(round(c,3) for c in (o.matrix_world@x.co)))
