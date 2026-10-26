import bpy, collections
asset=bpy.data.collections['Asset_walc']
for o in asset.all_objects:
 if o.type!='MESH': continue
 mats=[s.material.name if s.material else None for s in o.material_slots]
 if any(x for x in mats if x and not x.startswith(('WALC_Reference_Brick','WALC_Reference_Limestone','WALC_Reference_Glass'))):
  print(o.name, list(set(mats)))
