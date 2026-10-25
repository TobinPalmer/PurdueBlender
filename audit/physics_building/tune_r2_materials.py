import bpy
from pathlib import Path
p=Path.cwd()/'modular/buildings/physics_building_phys_3bf42f3.blend'; bpy.ops.wm.open_mainfile(filepath=str(p))
roof=bpy.data.objects['PHYS | estimated sloped red tile roof']; mat=bpy.data.materials['PHYSICS_BUILDING | evidence palette roof']; nt=mat.node_tree
brick=next(n for n in nt.nodes if n.type=='TEX_BRICK'); brick.inputs['Color1'].default_value=(.24,.038,.02,1); brick.inputs['Color2'].default_value=(.51,.14,.072,1); brick.inputs['Mortar'].default_value=(.17,.09,.065,1); brick.inputs['Mortar Size'].default_value=.026; brick.inputs['Mortar Smooth'].default_value=.02
bump=next(n for n in nt.nodes if n.type=='BUMP'); bump.inputs['Strength'].default_value=.32; bump.inputs['Distance'].default_value=.075
mat['roof_surface_note']='Contrasting terracotta tile and mortar colors with raised, GIS-axis-aligned staggered courses; visual color/pitch follow official Purdue facade photos, exact pitch remains estimated.'
metal=bpy.data.materials['PHYSICS_BUILDING | graphite metal details']; bs=next(n for n in metal.node_tree.nodes if n.type=='BSDF_PRINCIPLED'); bs.inputs['Base Color'].default_value=(.014,.022,.03,1); bs.inputs['Metallic'].default_value=.12; bs.inputs['Roughness'].default_value=.58
metal.diffuse_color=(.014,.022,.03,1)
asset=bpy.data.collections['Asset_physics_building']; asset['r2_material_revision']='Higher-contrast terracotta roof tiles and low-gloss charcoal window/door frames tuned against official exterior reference.'
bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True)
print('Updated roof tile contrast and sash frame finish.')
