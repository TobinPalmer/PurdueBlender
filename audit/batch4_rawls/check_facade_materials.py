import bpy
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend')
for n in ['RAWL_East_Windows_Glass','RAWL_North_Windows_Glass','RAWL_West_Windows_Glass','RAWL_South_Windows_East_Glass','RAWL_South_Windows_South_Glass','RAWL_SE_Diagonal_CurtainWall_Glass','RAWL_NW_Rotunda_Curved_CurtainWall']:
 o=bpy.data.objects.get(n)
 if o:print(n,[m.name for m in o.data.materials])
