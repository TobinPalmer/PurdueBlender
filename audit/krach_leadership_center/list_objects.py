import bpy
for o in bpy.data.objects:
 if o.type=='MESH': print(o.name, tuple(round(x,2) for x in o.dimensions),[m.name for m in o.data.materials if m])
