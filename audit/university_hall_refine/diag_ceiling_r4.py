import bpy
for o in bpy.data.objects:
 if 'ceiling' in o.name.lower() or 'floor' in o.name.lower() and (o.name.startswith('UNIV_') and ('R2' not in o.name and 'R4' not in o.name)):
  print(o.name,tuple(round(x,2) for x in o.matrix_world.translation),tuple(round(x,2) for x in o.dimensions),[m.name for m in o.data.materials] if o.type=='MESH' else '')
