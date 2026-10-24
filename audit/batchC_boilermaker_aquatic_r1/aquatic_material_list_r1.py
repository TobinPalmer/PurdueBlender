import bpy
for m in bpy.data.materials:
 if m.name.startswith('AQUA'): print(m.name)
