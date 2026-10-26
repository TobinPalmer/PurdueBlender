import bpy,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\rawls_hall.blend')
for o in bpy.context.scene.objects:
    if any(t.lower() in o.name.lower() for t in ['1086','desk','chair','lecture','lectern','screen','atrium','stair']):
       print(o.name,o.type,tuple(round(x,2) for x in o.location),tuple(round(x,2) for x in o.dimensions),o.data.name if o.data else '')
