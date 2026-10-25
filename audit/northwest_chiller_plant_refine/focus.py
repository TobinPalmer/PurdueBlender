import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='modular/buildings/northwest_chiller_plant.blend'); c=bpy.data.collections['Asset_northwest_chiller_plant']
for o in c.all_objects:
 if o.name in ['NWCP_service_double_door','NWCP_service_canopy','NWCP_building_identity_label','NWCP_roof_equipment_screen','northwest_chiller_plant_flat_roof_surface'] or o.name.startswith('NWCP_acoustic_louver_bank_0_0') or o.name.startswith('NWCP_roof_cooling_cell_'):
  pts=[o.matrix_world@Vector(v) for v in o.bound_box]; print(o.name, tuple(round(x,2) for x in [*(min(p[i] for p in pts) for i in range(3)),*(max(p[i] for p in pts) for i in range(3))]))
