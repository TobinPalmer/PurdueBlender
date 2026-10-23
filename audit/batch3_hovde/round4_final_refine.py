import bpy
from pathlib import Path

P = Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
f = P / 'modular/buildings/hovde_hall.blend'
bpy.ops.wm.open_mainfile(filepath=str(f))

# Reduce the bulky architrave while retaining its alignment with the six supports.
ent = bpy.data.objects['HOVD_Portico_Entablature']
ent.scale.z *= .58
ent.scale.y *= .76
ent.location.z = 10.80
corn = bpy.data.objects['HOVD_Portico_Cornice']
corn.location.z = 11.12
ped = bpy.data.objects['HOVD_Portico_Pediment_Base']
ped.location.z = 12.49
# Slightly slimmer columns give the central bays and their glazing more air.
for i in range(1, 7):
    shaft = bpy.data.objects[f'HOVD_Classical_Column_{i}']
    shaft.scale.x *= .84
    shaft.scale.y *= .84
    for part in ('HOVD_Column_Base_', 'HOVD_Column_Capital_'):
        o = bpy.data.objects[f'{part}{i}']
        o.scale.x *= .88
        o.scale.y *= .88

# Set the stone to a neutral, mid-value limestone so it reads clearly against the brick.
stone = bpy.data.materials['Bedford_Indiana_Limestone']
stone.diffuse_color = (.58, .55, .49, 1)
bs = stone.node_tree.nodes.get('Principled BSDF') if stone.node_tree else None
if bs:
    bs.inputs['Base Color'].default_value = (.58, .55, .49, 1)
    bs.inputs['Roughness'].default_value = .78

bpy.ops.wm.save_as_mainfile(filepath=str(f))
print('Saved final portico profile refinement; GIS shell and root placement unchanged.')
