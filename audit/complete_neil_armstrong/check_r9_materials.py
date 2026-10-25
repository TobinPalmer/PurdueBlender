import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\neil_armstrong_hall.blend')
for name in ['ARMS_R6_Mayflower_Red_ACM','ARMS_Purdue_Red_Brick','ARMS_Bedford_Limestone','ARMS_Mullion_Steel']:
 m=bpy.data.materials.get(name)
 print(name, tuple(m.diffuse_color) if m else None)
 if m and m.use_nodes:
  bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
  print(' base',tuple(bs.inputs['Base Color'].default_value) if bs else None)
