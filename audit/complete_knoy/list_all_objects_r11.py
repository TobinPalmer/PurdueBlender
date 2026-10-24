import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend')
for o in sorted(bpy.data.collections['Asset_knoy_hall'].objects,key=lambda x:x.name):print(o.name, o.type, len(o.data.vertices) if o.type=='MESH' else '')
