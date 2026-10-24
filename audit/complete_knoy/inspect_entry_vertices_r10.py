import bpy,collections
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend')
o=bpy.data.objects['KNOY_Entrances_And_Canopies'];
for i,v in enumerate(o.data.vertices):print(i,tuple(round(c,3) for c in v.co))
