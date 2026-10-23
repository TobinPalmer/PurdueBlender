import bpy
P=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/hovde_hall.blend';bpy.ops.wm.open_mainfile(filepath=P);c=bpy.data.collections['Asset_hovde_hall']
for o in c.all_objects:
 if o and any(t in o.name for t in ['Board_Table_Center','Board_Table_Ped','Chair_','Board_Gold']): print(o.name,tuple(round(v,2) for v in o.location),tuple(round(v,2) for v in o.dimensions))
