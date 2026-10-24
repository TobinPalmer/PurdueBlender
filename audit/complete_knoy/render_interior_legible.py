import bpy
from mathutils import Vector

ROOT = r'C:\Users\Tobin\Documents\Blender\PurdueMap'
BLEND = ROOT + r'\modular\buildings\knoy_hall.blend'
OUT = ROOT + r'\audit\complete_knoy\knoy_ground_interior_legible.png'
bpy.ops.wm.open_mainfile(filepath=BLEND)
scene = bpy.context.scene

# Isolate the saved first-floor shell and its traced interior. Keep the floor slab,
# partition walls, and illustrative door leaves; hide roof and upper-floor geometry.
for obj in scene.objects:
    obj.hide_render = obj.name.startswith((
        'KNOY_FloorSlab_Basement', 'KNOY_FloorSlab_L2', 'KNOY_FloorSlab_L3',
        'KNOY_FloorSlab_L4', 'KNOY_FloorSlab_L5', 'KNOY_FloorSlab_RoofDeck',
        'KNOY_Exterior_Masonry_Walls', 'KNOY_Fenestration',
        'KNOY_Entrances_And_Canopies', 'KNOY_Plaza', 'KNOY_Roof_',
        'KNOY_Structural_Columns', 'KNOY_L2_TypicalPlan', 'KNOY_L3_TypicalPlan',
        'KNOY_L4_TypicalPlan', 'KNOY_Stair_',
    ))

# Frame the unobstructed corridor between two raster-traced partition openings.
# The position is selected from the saved trace bounds; it is a presentation view,
# not a claim about the building's surveyed camera location.
camera_data = bpy.data.cameras.new('KNOY_Interior_Evidence_Camera')
camera = bpy.data.objects.new('KNOY_Interior_Evidence_Camera', camera_data)
scene.collection.objects.link(camera)
camera.location = (-6.2, -13.0, 1.62)
target = Vector((-3.98, -9.8, 1.62))
camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera_data.lens = 35
scene.camera = camera

# Soft neutral interior fill for a readable audit view; this is not saved into the
# building library and does not change the architectural material assignments.
world = scene.world
world.use_nodes = True
background = world.node_tree.nodes.get('Background')
background.inputs['Color'].default_value = (0.55, 0.58, 0.62, 1)
background.inputs['Strength'].default_value = 0.7
for obj in scene.objects:
    if obj.type == 'LIGHT':
        obj.hide_render = True
light_data = bpy.data.lights.new('KNOY_Interior_Evidence_Area', 'AREA')
light_data.energy = 900
light_data.shape = 'DISK'
light_data.size = 6
light = bpy.data.objects.new('KNOY_Interior_Evidence_Area', light_data)
scene.collection.objects.link(light)
light.location = (-1.0, -10.0, 4.8)
light.rotation_euler = (Vector((-4.0, -9.5, 1.0)) - light.location).to_track_quat('-Z', 'Y').to_euler()
light_data2 = bpy.data.lights.new('KNOY_Interior_Evidence_Area_Fill', 'AREA')
light_data2.energy = 700
light_data2.shape = 'DISK'
light_data2.size = 5
light2 = bpy.data.objects.new('KNOY_Interior_Evidence_Area_Fill', light_data2)
scene.collection.objects.link(light2)
light2.location = (-5.8, -5.0, 4.2)
light2.rotation_euler = (Vector((-4.0, -8.0, 1.0)) - light2.location).to_track_quat('-Z', 'Y').to_euler()

# Audit-only neutral overrides make the traced room volumes and openings legible.
# They are not saved into the source asset and do not claim actual finish colors.
def audit_mat(name, color, roughness=0.82):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = roughness
    return m

wall_mat = audit_mat('KNOY_Audit_Neutral_Wall', (0.78, 0.79, 0.80))
floor_mat = audit_mat('KNOY_Audit_Neutral_Floor', (0.34, 0.36, 0.38))
door_mat = audit_mat('KNOY_Audit_Door_Leaf_Contrast', (0.30, 0.21, 0.14))
for obj in scene.objects:
    if obj.type != 'MESH':
        continue
    if obj.name.startswith('KNOY_Ground_TracePartition_'):
        obj.data.materials.clear()
        obj.data.materials.append(wall_mat)
    elif obj.name == 'KNOY_FloorSlab_L1_Ground':
        obj.data.materials.clear()
        obj.data.materials.append(floor_mat)
    elif obj.name.startswith('KNOY_Illustrative_Door_'):
        obj.data.materials.clear()
        obj.data.materials.append(door_mat)

scene.render.engine = 'CYCLES'
scene.cycles.samples = 48
scene.cycles.use_denoising = True
scene.render.resolution_x = 1500
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
scene.render.filepath = OUT
scene.view_settings.view_transform = 'AgX'
scene.render.image_settings.color_mode = 'RGBA'
bpy.ops.render.render(write_still=True)
print('WROTE', OUT)
