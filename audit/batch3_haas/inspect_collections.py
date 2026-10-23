import bpy
c=bpy.data.collections['Asset_felix_haas_hall']
print('direct',len(c.objects))
for o in c.objects:
 if 'Portal' in o.name or 'Entry' in o.name or 'Step' in o.name or 'StonePanel' in o.name or 'Limestone_Facade' in o.name:print(o.name,[x.name for x in o.users_collection])
for n in ['Reference_Incompatible_Geometry_felix_haas_hall']:
 x=bpy.data.collections.get(n);print('archive hidden',x.hide_render,x.hide_viewport,'direct',len(x.objects))
