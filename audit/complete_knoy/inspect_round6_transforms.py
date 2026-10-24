import bpy,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/complete_knoy/knoy_hall_round6_candidate.blend')
for n in ['AssetRoot_knoy_hall','KNOY_Roof_PV_28Panel_Array_R6','KNOY_FloorSlab_RoofDeck','KNOY_Roof_Mechanical_Penthouse']:
 o=bpy.data.objects.get(n)
 if o: print(n,'loc',list(o.location),'worldloc',list(o.matrix_world.translation),'parent',o.parent.name if o.parent else None,'matrix',[[round(v,3) for v in row] for row in o.matrix_world])
