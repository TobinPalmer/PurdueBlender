import bpy
bpy.ops.wm.open_mainfile(filepath='modular/buildings/massing_house_301841603_654031c.blend')
o=bpy.data.objects['House_301841603']
print('vertices')
for v in o.data.vertices:
 print(tuple(round(x,3) for x in o.matrix_world@v.co))
