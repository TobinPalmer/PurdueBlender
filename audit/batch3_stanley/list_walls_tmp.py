import bpy
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend';bpy.ops.wm.open_mainfile(filepath=p)
for o in bpy.data.collections['SC_Exterior_Structure'].objects: print(o.name)
