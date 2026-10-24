import bpy
from pathlib import Path
ROOT=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
asset=ROOT/'modular/buildings/krannert_building.blend'
bpy.ops.wm.open_mainfile(filepath=str(asset))
mat=bpy.data.materials['KRAN_Purdue_Red_Brick_R4']
mat.diffuse_color=(.20,.065,.045,1)
bsdf=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
tex=mat.node_tree.nodes.get('R4_Brick_And_Mortar')
tex.inputs['Color1'].default_value=(.20,.065,.045,1)
tex.inputs['Color2'].default_value=(.27,.095,.062,1)
tex.inputs['Mortar'].default_value=(.12,.115,.105,1)
bsdf.inputs['Roughness'].default_value=.9
mat['round4_note']='Darkened red-brown procedural brick after comparison with undated Purdue exterior photo; hue/brick scale remain visual estimates.'
bpy.ops.wm.save_as_mainfile(filepath=str(asset))
print('Updated saved source brick tone only; no mesh geometry changed.')
