import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend')
for name in ['KNOY_FloorSlab_Basement','KNOY_FloorSlab_L1_Ground','KNOY_FloorSlab_L2','KNOY_FloorSlab_L3','KNOY_FloorSlab_L4','KNOY_FloorSlab_L5','KNOY_FloorSlab_RoofDeck']:
 o=bpy.data.objects.get(name)
 pts=[o.matrix_world @ Vector(v) for v in o.bound_box]
 bounds=[[round(min(p[i] for p in pts),3),round(max(p[i] for p in pts),3)] for i in range(3)]
 print(name,bounds)
