import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\owen_hall.blend')
for o in bpy.data.objects:
 if o.name=='AssetRoot_owen_hall' or o.name=='Owen_NW_Wing_Limestone_Base':
  print(o.name,'loc',tuple(o.location),'world',tuple(o.matrix_world.translation),'dims',tuple(o.dimensions),'parent',o.parent)
