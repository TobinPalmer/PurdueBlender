import bpy
for o in bpy.data.collections['Asset_lawson_hall'].objects:
 if 'R3' in o.name or 'R4' in o.name or 'R5' in o.name:
  p=o.matrix_world.translation
  print(o.name, o.type, tuple(round(v,3) for v in p), tuple(round(v,3) for v in o.dimensions),len(o.data.vertices) if o.type=='MESH' else '')
