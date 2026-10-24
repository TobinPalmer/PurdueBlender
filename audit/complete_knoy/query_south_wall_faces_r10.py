import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend')
o=bpy.data.objects['KNOY_Exterior_Masonry_Walls'];
vals=[]
for p in o.data.polygons:
 c=o.matrix_world@p.center
 if abs(c.y+46.58)<2: vals.append((p.index,tuple(round(v,2) for v in c),tuple(round(v,2) for v in (o.matrix_world.to_3x3()@p.normal)),o.data.materials[p.material_index].name))
print(len(vals));print(vals[:40])
