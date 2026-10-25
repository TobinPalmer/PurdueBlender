import bpy
c=bpy.data.collections['Asset_stewart_center']
for o in sorted(c.all_objects,key=lambda x:x.name)[:250]:
 print(o.name, o.type)
