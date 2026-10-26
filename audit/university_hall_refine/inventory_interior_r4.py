import bpy
for o in sorted(bpy.data.collections['Asset_university_hall'].all_objects,key=lambda o:o.name):
 if any(s in o.name.lower() for s in ('interior','gallery','overlook','stair','column','balustrade')):
  print(o.name, 'hide', o.hide_render, 'loc', tuple(round(v,2) for v in o.location), 'dims', tuple(round(v,2) for v in o.dimensions))
