import bpy, json
from mathutils import Vector
objs=[]
for o in bpy.data.objects:
 if any(s.lower() in o.name.lower() for s in ('roof','mansard','r4_','dormer','spire','belfry')):
  o.update_tag()
  pts=[o.matrix_world@Vector(c) for c in o.bound_box] if o.type=='MESH' else []
  bbox=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)] if pts else None
  objs.append({'name':o.name,'type':o.type,'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'location':list(o.location),'dimensions':list(o.dimensions),'bounds':bbox,'parent':o.parent.name if o.parent else None})
print(json.dumps(objs,indent=2))
