import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend')
for mn in ['KNOY_Precast_Concrete','KNOY_Dark_Tinted_Glass']:
 m=bpy.data.materials[mn]; print(mn)
 for n in m.node_tree.nodes:
  if n.type in ['MIX','BUMP','TEX_NOISE','BSDF_PRINCIPLED']:
   print(n.name,n.type,[(s.name,s.default_value) for s in n.inputs if hasattr(s,'default_value')])
