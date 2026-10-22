import bpy
for o in bpy.data.collections['Asset_armory'].all_objects:
 if o.type=='MESH' and any(s.material and s.material.name=='Solar_Ribbon_Glass' for s in o.material_slots):
  if 'Window_East_Low_-36' in o.name or 'Tower' in o.name:print(o.name,tuple(o.location),tuple(o.dimensions))
for o in bpy.data.collections['Asset_armory'].all_objects:
 if 'Tower' in o.name or 'Corner' in o.name:print(o.name,tuple(o.location),tuple(o.dimensions),[s.material.name for s in o.material_slots if s.material])
