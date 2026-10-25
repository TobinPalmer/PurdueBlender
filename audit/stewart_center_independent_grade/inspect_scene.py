import bpy, collections, json
c=bpy.data.collections['Asset_stewart_center']
objs=list(c.all_objects)
print('COUNTS')
for prefix,n in collections.Counter('_'.join(o.name.split('_')[:2]) for o in objs).most_common(100): print(prefix,n)
print('PREFIX STEW')
for o in sorted(objs,key=lambda o:o.name):
 if o.name.startswith('STEW_'):
  print(o.name, o.type, [round(v,2) for v in o.dimensions], [round(v,2) for v in o.location])
