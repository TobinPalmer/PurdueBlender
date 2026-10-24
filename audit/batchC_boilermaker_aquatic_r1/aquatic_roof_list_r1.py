import bpy
asset=bpy.data.collections['Asset_morgan_j_burke_boilermaker_aquatic_center']
for o in asset.all_objects:
 if o.type=='MESH' and any(t in o.name.lower() for t in ('roof','gable')): print(o.name, [c.name for c in o.users_collection])
