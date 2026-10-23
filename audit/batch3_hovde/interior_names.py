import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/hovde_hall.blend');c=bpy.data.collections['Asset_hovde_hall']
for o in c.all_objects:
 if o and ('Chair' in o.name or 'Board' in o.name or 'Trust' in o.name): print(o.name, o.parent.name if o.parent else '-', tuple(round(a,1) for a in o.location),tuple(round(a,1) for a in o.dimensions))
