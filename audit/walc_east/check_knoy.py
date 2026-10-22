import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/knoy_hall.blend')
for o in bpy.data.objects:
 if o.type=='MESH':print(o.name,o.hide_render,o.hide_viewport,len(o.data.vertices),o.matrix_world.translation[:],o.scale[:])
