import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend')
for n in ['RAWL_Masonry_Exterior_Walls','RAWL_North_Windows_Glass','RAWL_North_Windows_BronzeMullions','RAWL_North_Windows_LimestoneSills','RAWL_SE_Diagonal_CurtainWall_Glass','RAWL_SE_Diagonal_CurtainWall_BronzeMullions']:
 o=bpy.data.objects[n];p=[o.matrix_world@Vector(c) for c in o.bound_box];bb=[[round(min(v[i] for v in p),2),round(max(v[i] for v in p),2)] for i in range(3)];print(n,bb,'vertices',len(o.data.vertices),'mat', [m.name for m in o.data.materials])
