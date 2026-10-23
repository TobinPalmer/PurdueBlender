import bpy
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend')
for o in bpy.data.objects:
 if 'Window' in o.name and any(k in o.name.lower() for k in ['glass','glaz','mullion']):
  print(o.name,o.type,len(o.data.polygons) if o.type=='MESH' else 0, [round(o.matrix_world@__import__('mathutils').Vector(v)[i],2) for i in range(3)] if False else '')
