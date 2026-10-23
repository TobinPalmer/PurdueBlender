import bpy
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');f=P/'modular/buildings/hovde_hall.blend';bpy.ops.wm.open_mainfile(filepath=str(f))
# Darker red-brown brick at both the procedural texture and preview/material level.
m=bpy.data.materials['Purdue_Red_Brick'];m.diffuse_color=(.25,.052,.022,1);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.25,.052,.022,1)
for n in m.node_tree.nodes:
 if n.bl_idname=='ShaderNodeTexBrick':
  n.inputs['Color1'].default_value=(.29,.065,.028,1);n.inputs['Color2'].default_value=(.19,.038,.017,1);n.inputs['Mortar'].default_value=(.105,.072,.052,1)
# Limestone moves away from blown-out ivory to neutral warm grey.
m=bpy.data.materials['Bedford_Indiana_Limestone'];m.diffuse_color=(.52,.49,.43,1);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.52,.49,.43,1)
ramp=next((n for n in m.node_tree.nodes if n.bl_idname=='ShaderNodeValToRGB'),None)
if ramp:ramp.color_ramp.elements[0].color=(.46,.44,.39,1);ramp.color_ramp.elements[1].color=(.56,.53,.47,1)
# Roof material has terracotta depth; increase tile size so courses read at building scale.
m=bpy.data.materials['Hovde_Roof_Membrane'];m.diffuse_color=(.12,.025,.01,1);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.78
for n in m.node_tree.nodes:
 if n.bl_idname=='ShaderNodeTexBrick':
  n.inputs['Color1'].default_value=(.20,.04,.016,1);n.inputs['Color2'].default_value=(.135,.024,.009,1);n.inputs['Mortar'].default_value=(.065,.035,.02,1);n.inputs['Scale'].default_value=48;n.inputs['Brick Width'].default_value=.5;n.inputs['Row Height'].default_value=.28;n.inputs['Mortar Size'].default_value=.006
# Blue-grey reflective glazing and dark sash remain visibly distinct.
m=bpy.data.materials['Solar_Ribbon_Glass'];m.diffuse_color=(.075,.14,.18,1);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.075,.14,.18,1);bs.inputs['Metallic'].default_value=.16;bs.inputs['Roughness'].default_value=.18
# Save edits in assigned Hovde file.
bpy.ops.wm.save_as_mainfile(filepath=str(f));print('updated authored facade/roof values')
