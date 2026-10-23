import bpy
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend')
o=bpy.data.objects['RAWL_FloorSlab_L1_Ground']
for p in o.data.polygons:
 c=o.matrix_world@p.center
 n=o.matrix_world.to_3x3()@p.normal
 print(round(c.x,1),round(c.y,1),round(c.z,2),round(n.z,2),round(p.area,2),p.material_index)
