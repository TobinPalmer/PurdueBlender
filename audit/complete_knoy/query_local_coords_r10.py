import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend')
for n in ['KNOY_Exterior_Masonry_Walls','KNOY_Entrances_And_Canopies','KNOY_Plaza_Paving_And_Site']:
 o=bpy.data.objects[n];pts=[o.matrix_world@v.co for v in o.data.vertices]
 print(n,'loc',tuple(o.location),'local extrema',[(min(v[i] for v in pts),max(v[i] for v in pts)) for i in range(3)])
