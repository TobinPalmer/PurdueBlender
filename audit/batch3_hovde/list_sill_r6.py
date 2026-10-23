import bpy
bpy.ops.wm.open_mainfile(filepath='modular/buildings/hovde_hall.blend');c=bpy.data.collections['Asset_hovde_hall']
for o in sorted(c.all_objects,key=lambda x:x.name):
 if o and any(k in o.name.lower() for k in ['sill','lintel','window_jamb','reveal']): print(o.name,tuple(round(v,2) for v in o.location),tuple(round(v,2) for v in o.dimensions))
