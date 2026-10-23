import bpy
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');f=P/'modular/buildings/hovde_hall.blend';bpy.ops.wm.open_mainfile(filepath=str(f));w=bpy.context.scene.world
bg=next((n for n in w.node_tree.nodes if n.bl_idname=='ShaderNodeBackground'),None);bg.inputs['Color'].default_value=(.40,.40,.40,1);bg.inputs['Strength'].default_value=.75;w.color=(.4,.4,.4)
bpy.ops.wm.save_as_mainfile(filepath=str(f));print('balanced neutral ambient background')
