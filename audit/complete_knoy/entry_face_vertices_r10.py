import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend')
o=bpy.data.objects['KNOY_Exterior_Masonry_Walls'];
for idx in [829,830,831,832]:
 p=o.data.polygons[idx];print(idx,o.data.materials[p.material_index].name,[tuple(round(c,2) for c in o.data.vertices[i].co) for i in p.vertices])
