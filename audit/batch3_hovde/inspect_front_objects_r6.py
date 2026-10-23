import bpy
bpy.ops.wm.open_mainfile(filepath='modular/buildings/hovde_hall.blend'); c=bpy.data.collections['Asset_hovde_hall']
for o in sorted(c.all_objects,key=lambda x:(x.location.y,x.name)):
 if o and abs(o.location.y+35.15)<3.0 and -1<o.location.z<17.5:
  print(o.name,o.type,tuple(round(v,2) for v in o.location),tuple(round(v,2) for v in o.dimensions),[m.name for m in o.data.materials] if o.type=='MESH' else '')
