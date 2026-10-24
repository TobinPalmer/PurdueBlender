import bpy, os
from mathutils import Vector

ROOT = r'C:/Users/Tobin/Documents/Blender/PurdueMap'
ASSET = ROOT + '/modular/buildings/krannert_building.blend'
OUT = ROOT + '/audit/batch2_krannert'
bpy.ops.wm.open_mainfile(filepath=ASSET)
s = bpy.context.scene
s.render.engine = 'CYCLES'
s.cycles.samples = 24
s.cycles.use_denoising = True
s.render.resolution_x = 1400
s.render.resolution_y = 900
s.render.resolution_percentage = 100
s.world.use_nodes = True
bg = s.world.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value = (.62,.69,.79,1)
bg.inputs['Strength'].default_value = .55

# Hide the unsupported square source-library paving plate for this audit render.
# The neutral ground plane is render-only, has no claimed pavement/road layout,
# and represents the local z=0 context that the campus master should supply.
pad = bpy.data.objects.get('KRAN_Surrounding_Plaza_Paving')
if pad:
    pad.hide_render = True

mat = bpy.data.materials.new('R3_RenderOnly_Neutral_Ground')
mat.diffuse_color = (.27,.29,.28,1)
mat.use_nodes = True
bs = mat.node_tree.nodes.get('Principled BSDF')
bs.inputs['Base Color'].default_value = (.27,.29,.28,1)
bs.inputs['Roughness'].default_value = .98
bpy.ops.mesh.primitive_plane_add(size=240, location=(0,0,-.03))
ground = bpy.context.object
ground.name = 'R3_RENDER_ONLY_GRADE_PLANE'
ground.data.materials.append(mat)

for cam_name, out_name in [
    ('Cam_KRAN_02_SW_StateSt_Entrance','krannert_exterior_front_r3.png'),
    ('Cam_KRAN_03_SE_GrantSt_Corner','krannert_courtyard_corner_r3.png'),
]:
    cam = bpy.data.objects.get(cam_name)
    if not cam:
        raise RuntimeError('Missing source camera: ' + cam_name)
    s.camera = cam
    s.render.filepath = os.path.join(OUT, out_name)
    bpy.ops.render.render(write_still=True)

print('RENDER_ONLY_GROUND; asset not saved; source paving hidden only for these views')
