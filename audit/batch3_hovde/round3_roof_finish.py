import bpy
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');f=P/'modular/buildings/hovde_hall.blend';bpy.ops.wm.open_mainfile(filepath=str(f));
m=bpy.data.materials['Hovde_Roof_Membrane']
for n in m.node_tree.nodes:
 if n.bl_idname=='ShaderNodeTexBrick':
  n.inputs['Color1'].default_value=(.13,.025,.009,1);n.inputs['Color2'].default_value=(.085,.014,.005,1);n.inputs['Mortar'].default_value=(.045,.025,.013,1)
m.diffuse_color=(.10,.02,.007,1)
# Blend the small, explicitly estimated roof-access enclosure into the surrounding masonry.
p=bpy.data.objects['HOVD_Penthouse'];p.data.materials.clear();p.data.materials.append(bpy.data.materials['Purdue_Red_Brick'])
# Keep its louvers readable but subdued.
l=bpy.data.objects['HOVD_Penthouse_Louvers'];l.data.materials.clear();l.data.materials.append(bpy.data.materials['Hovde_Bronze_Metal'])
bpy.ops.wm.save_as_mainfile(filepath=str(f));print('darkened clay tile and reduced penthouse contrast')
