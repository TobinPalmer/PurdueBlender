import bpy,os
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\rawls_hall.blend')
arr=[]
for o in bpy.data.objects:
 if o.type=='MESH':
  dims=tuple(abs(o.matrix_world.to_scale()[i])*o.dimensions[i] for i in range(3))
  arr.append((max(dims),o.name,tuple(round(x,2) for x in o.location),tuple(round(x,2) for x in dims),o.hide_render))
for x in sorted(arr,reverse=True)[:35]: print(x)
