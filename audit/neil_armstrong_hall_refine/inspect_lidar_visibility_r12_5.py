import bpy,json
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\neil_armstrong_hall.blend')
print(json.dumps([{'name':o.name,'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'hide_get':o.hide_get(),'display_type':o.display_type,'hide_set':o.hide_get(),'materials':[m.name for m in o.data.materials if m]} for o in bpy.data.objects if 'Coarse_LiDAR' in o.name],indent=2))
