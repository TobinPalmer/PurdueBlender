import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend')
for name in ['KNOY_Exterior_Masonry_Walls','KNOY_Entrances_And_Canopies','KNOY_Footprint_Reference_Wire','KNOY_Plaza_Paving_And_Site']:
 o=bpy.data.objects[name];p=o.parent
 print(name,'parent',p.name if p else None,'parent loc',tuple(p.location) if p else None,'matrixworld loc',tuple(o.matrix_world.translation),'loc',tuple(o.location),'scale',tuple(o.scale))
