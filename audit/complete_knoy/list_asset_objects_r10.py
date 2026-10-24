import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend')
for o in sorted(bpy.data.collections['Asset_knoy_hall'].objects,key=lambda o:o.name):print(o.name,o.type,tuple(round(v,2) for v in o.dimensions),tuple(round(v,2) for v in o.location))
