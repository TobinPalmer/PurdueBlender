import bpy
for o in sorted(bpy.data.collections['Asset_university_hall'].all_objects,key=lambda o:o.name):
 if any(s in o.name for s in ('Wall_East','Wall_South','Wall_West','Wall_North')):
  print(o.name,o.type,tuple(round(v,2) for v in o.dimensions),o.hide_render)
