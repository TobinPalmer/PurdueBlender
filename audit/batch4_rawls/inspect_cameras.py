import bpy
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend')
for o in bpy.data.objects:
 if o.type=='CAMERA':print(o.name,o.location[:],o.rotation_euler[:],o.data.type,o.data.ortho_scale if o.data.type=='ORTHO' else o.data.lens)
