import bpy
for o in bpy.context.scene.objects:
 if o.type=='MESH' and any(k in o.name.lower() for k in ('roof','penthouse')):
  print('OBJECT',o.name,'dims',tuple(round(v,1) for v in o.dimensions),'z',round(o.location.z,2),'slots',[(i,m.name if m else None) for i,m in enumerate(o.data.materials)])
  if len(o.data.materials)>1:
   from collections import Counter
   print(' POLY_MAT_COUNTS',Counter(p.material_index for p in o.data.polygons))
