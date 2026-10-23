import bpy
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');f=P/'modular/buildings/hovde_hall.blend';bpy.ops.wm.open_mainfile(filepath=str(f));root=bpy.data.objects['HOVD_Root'];c=bpy.data.collections['Asset_hovde_hall']
prefixes=('HOVD_Classical_Column_','HOVD_Column_Base_','HOVD_Column_Capital_','HOVD_Roof_TileHint_','HOVD_Pres_Room_','HOVD_Board_Room_')
for o in c.all_objects:
 if o and o.name.startswith(prefixes) and o.parent is None:
  o.parent=root;o.matrix_parent_inverse.identity()
  print('parented',o.name)
# stronger red tile tone while retaining rough matte surface
m=bpy.data.materials['Hovde_Roof_Membrane'];m.diffuse_color=(.22,.025,.012,1);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.22,.025,.012,1);bs.inputs['Roughness'].default_value=.78
bpy.ops.wm.save_as_mainfile(filepath=str(f));print('saved parent repair')
