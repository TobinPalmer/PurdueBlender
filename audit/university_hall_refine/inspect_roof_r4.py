import bpy
for o in sorted(bpy.data.collections['Asset_university_hall'].all_objects,key=lambda o:o.name):
 if any(s in o.name.lower() for s in ('roof','mansard','ridge','dormer')):
  print(o.name,'type',o.type,'loc',tuple(round(v,2) for v in o.location),'dims',tuple(round(v,2) for v in o.dimensions),'hide',o.hide_render)
