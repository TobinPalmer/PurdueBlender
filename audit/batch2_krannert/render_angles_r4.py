import bpy, os
from mathutils import Vector

ROOT = r'C:/Users/Tobin/Documents/Blender/PurdueMap'
ASSET = ROOT + '/modular/buildings/krannert_building.blend'
OUT = ROOT + '/audit/batch2_krannert'
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 20
scene.cycles.use_denoising = True
scene.render.resolution_x = 1100
scene.render.resolution_y = 800
scene.render.resolution_percentage = 100
scene.world.use_nodes = True
bg = scene.world.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value = (.68,.73,.82,1)
bg.inputs['Strength'].default_value = .45

# Render-only neutral ground. It carries no claimed road/sidewalk materials.
mat = bpy.data.materials.new('R4_RenderOnly_Neutral_Ground')
mat.diffuse_color = (.27,.29,.28,1)
mat.use_nodes = True
mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value = (.27,.29,.28,1)
mat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value = .98
bpy.ops.mesh.primitive_plane_add(size=220, location=(234.5,-411.5,-.03))
bpy.context.object.name = 'R4_RENDER_ONLY_GRADE_PLANE'
bpy.context.object.data.materials.append(mat)
root = bpy.data.objects['AssetRoot_krannert_building']
bpy.context.object.parent = root

# Use the saved source cameras exactly as stored under the asset root so the
# geometry and view retain the established coordinate frame.
for cam_name, out_name in [
    ('Cam_KRAN_02_SW_StateSt_Entrance','krannert_southwest_legacy_r4.png'),
    ('Cam_KRAN_03_SE_GrantSt_Corner','krannert_southeast_exterior_corner_r4.png'),
    ('Cam_KRAN_04_East_Skywalk_Dock','krannert_east_grant_corner_r4.png'),
]:
    scene.camera = bpy.data.objects[cam_name]
    scene.render.filepath = os.path.join(OUT,out_name)
    bpy.ops.render.render(write_still=True)

print('Fresh saved-source renders with the existing cameras; temporary grade plane was not saved.')
