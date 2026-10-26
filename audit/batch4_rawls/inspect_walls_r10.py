import bpy, math
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\rawls_hall.blend')
for nm in ['RAWL_2026_Plan1086_00_00','RAWL_2026_Plan1086_01_00','RAWL_2026_Plan1086_02_00','RAWL_2026_Plan1086_03_00','RAWL_2026_Plan1086_04_00']:
 o=bpy.data.objects[nm]; print(nm,'rot',tuple(round(v,3) for v in o.rotation_euler),'location',tuple(round(v,2) for v in o.matrix_world.translation))
 pts=[o.matrix_world@v.co for v in o.data.vertices]; print('bounds',[(round(min(p[i] for p in pts),2),round(max(p[i] for p in pts),2)) for i in range(3)])
