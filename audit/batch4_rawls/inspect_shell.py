import bpy
for o in bpy.data.objects:
 if any(t in o.name.lower() for t in ['roof','floor','masonry','apron','windows','rotunda','curtain','foundation']):
  if o.name.startswith('RAWL_'):
   print(o.name, 'type',o.type,'hide_render',o.hide_render,'loc',tuple(round(x,2) for x in o.location),'mw',tuple(round(x,2) for x in o.matrix_world.translation),'parent',o.parent.name if o.parent else None)
