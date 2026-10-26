import bpy
for o in bpy.data.objects:
 if 'ceiling' in o.name.lower() or 'gallery' in o.name.lower() or 'floor_' in o.name.lower() and 'univ_r4' not in o.name.lower():
  print(o.name,'loc',tuple(round(x,2) for x in o.matrix_world.translation),'dims',tuple(round(x,2) for x in o.dimensions),'hide',o.hide_render)
