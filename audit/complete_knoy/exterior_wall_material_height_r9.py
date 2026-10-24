import bpy,collections,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend')
o=bpy.data.objects['KNOY_Exterior_Masonry_Walls']; rows=collections.defaultdict(lambda:collections.Counter())
for p in o.data.polygons:
 c=o.matrix_world@p.center; n=o.matrix_world.to_3x3()@p.normal
 z=round(c.z*2)/2; material=o.data.materials[p.material_index].name if p.material_index<len(o.data.materials) else 'none'
 area=p.area*o.matrix_world.to_3x3().determinant()**(2/3)
 rows[z][material]+=area
for z,c in sorted(rows.items()): print(z,dict(c))
