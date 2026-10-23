import bpy
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend')
for o in bpy.data.objects:
 if any(x in o.name.lower() for x in ['stair','atrium','bridge','rail','roof_arched']):print(o.name,o.type)
