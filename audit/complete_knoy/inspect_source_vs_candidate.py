import bpy,json
from mathutils import Vector
for fp in [r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/knoy_hall.blend',r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/complete_knoy/knoy_hall_round6_candidate.blend']:
 bpy.ops.wm.open_mainfile(filepath=fp)
 print('FILE',fp)
 for n in ['AssetRoot_knoy_hall','KNOY_Roof_Solar_Photovoltaic_Array','KNOY_FloorSlab_RoofDeck']:
  o=bpy.data.objects.get(n)
  if o: print(n,'loc',list(o.location),'matrix_parent_inverse',[[round(v,3) for v in row] for row in o.matrix_parent_inverse],'matrix_basis',[[round(v,3) for v in row] for row in o.matrix_basis],'matrix_world',[[round(v,3) for v in row] for row in o.matrix_world],'parent',o.parent.name if o.parent else None)
