import bpy, os
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'))
for o in bpy.data.objects:
 n=o.name.lower()
 if any(w in n for w in ['core','stair','atrium','1086','door','entry']):print(o.name,tuple(round(q,2) for q in o.location),o.type)
