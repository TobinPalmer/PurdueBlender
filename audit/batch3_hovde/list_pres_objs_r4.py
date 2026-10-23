import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/hovde_hall.blend');c=bpy.data.collections['Asset_hovde_hall']
for o in c.all_objects:
 if o and o.name.startswith('HOVD_Pres_'): print(o.name,o.type,tuple(round(v,2) for v in o.location),tuple(round(v,2) for v in o.dimensions),'hide',o.hide_render)
