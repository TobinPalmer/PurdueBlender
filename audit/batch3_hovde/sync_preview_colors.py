import bpy
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');path=P/'modular/buildings/hovde_hall.blend';bpy.ops.wm.open_mainfile(filepath=str(path))
updates=[]
for m in bpy.data.materials:
 if not m.use_nodes or not m.node_tree:continue
 bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
 if not bs:continue
 base=bs.inputs['Base Color'].default_value
 if m.name not in {'Purdue_Red_Brick','Bedford_Indiana_Limestone'}:
  m.diffuse_color=tuple(base)
  updates.append({'name':m.name,'diffuse_color':list(m.diffuse_color)})
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path));assert len(bpy.data.collections['Asset_hovde_hall'].all_objects)==638
(P/'audit/batch3_hovde/material_sync.json').write_text(__import__('json').dumps(updates,indent=2))
print('SAVED_REOPENED; synced material preview colors',len(updates),'assets',len(bpy.data.collections['Asset_hovde_hall'].all_objects))
