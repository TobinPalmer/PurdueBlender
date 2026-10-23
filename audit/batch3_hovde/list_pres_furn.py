import bpy
bpy.ops.wm.open_mainfile(filepath='modular/buildings/hovde_hall.blend')
c=bpy.data.collections['Asset_hovde_hall']
for o in sorted(c.all_objects,key=lambda x:x.name):
 if any(x in o.name for x in ['Pres','Chesterfield']): print(o.name, tuple(round(v,1) for v in o.location), tuple(round(v,1) for v in o.dimensions))
