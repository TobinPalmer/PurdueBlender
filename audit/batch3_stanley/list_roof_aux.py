import bpy
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend';bpy.ops.wm.open_mainfile(filepath=p)
for o in bpy.data.objects:
 if any(k in o.name.lower() for k in ['chimney','roof','dormer']):print(o.name,'in',[(c.name) for c in o.users_collection],'hide',o.hide_render)
