import bpy
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend')
for n in ['RAWL_2026_Plan1086_04_00','RAWL_2026_Plan1086_05_00','RAWL_2026_PlanNWVestibule_03_00','RAWL_2026_PlanNWVestibule_00_00']:
 o=bpy.data.objects.get(n); print(n,tuple(round(v,2) for v in o.location),tuple(round(v,2) for v in o.dimensions),tuple(round(v,2) for v in o.bound_box[0]))
