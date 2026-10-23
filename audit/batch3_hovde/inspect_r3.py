import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/hovde_hall.blend');c=bpy.data.collections['Asset_hovde_hall']
for o in c.all_objects:
 if o and any(k in o.name.lower() for k in ('pent','roof','pres_','board_')): print(o.name,o.type,tuple(round(x,2) for x in o.location),tuple(round(x,2) for x in o.dimensions),tuple(round(x,2) for x in o.matrix_world.translation),o.parent.name if o.parent else '-')
