import bpy
bpy.ops.wm.open_mainfile(filepath='modular/buildings/hovde_hall.blend'); c=bpy.data.collections['Asset_hovde_hall']
for o in sorted(c.all_objects,key=lambda x:x.name):
 if o and o.type=='MESH':
  mats=[m.name for m in o.data.materials]
  if any('Glass' in m or 'Bronze' in m for m in mats) and ('Window' in o.name or o.name.startswith('HOVD_')):
   print(o.name,tuple(round(v,2) for v in o.location),tuple(round(v,2) for v in o.dimensions),mats)
