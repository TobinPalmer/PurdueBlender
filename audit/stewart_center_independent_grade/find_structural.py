import bpy
for o in sorted(bpy.data.collections['Asset_stewart_center'].all_objects,key=lambda x:x.name):
 if any(k in o.name for k in ['Ext_Wall','Roof','Foundation','Planter','Entry','Window','Stair','Facade']): print(o.name,o.type)
