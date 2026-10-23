import bpy
from mathutils import Vector
for n in ['HAAS_Brick_Wall_North','HAAS_Brick_Wall_South','HAAS_Brick_Wall_West']:
 o=bpy.data.objects.get(n);print(n,o.hide_render,o.hide_viewport,o.location[:],o.rotation_euler[:],o.dimensions[:],len(o.data.polygons),[m.name for m in o.data.materials])
