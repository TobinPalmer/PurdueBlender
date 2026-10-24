import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend')
s=bpy.context.scene
for k in s.keys():print(k,repr(s[k]))
for n in ['KNOY_FloorSlab_L5','KNOY_Exterior_Masonry_Walls']:
 o=bpy.data.objects.get(n); print('OBJ',n,dict(o.items()))
