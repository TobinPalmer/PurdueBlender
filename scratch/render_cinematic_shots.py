import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Vector

ROOT = Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
OUT = ROOT / 'renders' / 'cinematic'
OUT.mkdir(parents=True, exist_ok=True)
MANIFEST = json.loads((ROOT / 'modular' / 'manifest.json').read_text())
walc_asset = next(item for item in MANIFEST['assets'] if item['id'] == 'walc')

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def link_collection(path, name):
    with bpy.data.libraries.load(str(path), link=True) as (source, target):
        target.collections = [name]
    collection = target.collections[0]
    scene.collection.children.link(collection)
    return collection


# These are the current, independently maintained site patch and WALC asset.
link_collection(ROOT / 'modular' / 'site' / 'engineering_mall_groundwork_patch.blend',
                'Engineering_Mall_Groundwork_Patch')
walc_collection = link_collection(ROOT / 'modular' / walc_asset['file'], walc_asset['collection'])
walc_instance = bpy.data.objects.new('WALC placement', None)
walc_instance.instance_type = 'COLLECTION'
walc_instance.instance_collection = walc_collection
walc_instance.location = (*walc_asset['placement_origin_xy_m'], 0)
scene.collection.objects.link(walc_instance)

# The source fountain is authored north of the mapped Engineering Fountain anchor.
# Apply the same audited offset used by the Engineering Mall preview.
site_path = ROOT / 'modular' / 'site' / 'campus_site.blend'
with bpy.data.libraries.load(str(site_path), link=False) as (source, target):
    source_names = [name for name in source.objects
                    if name.lower().startswith(('engfountain_', 'engineering_fountain_', 'fountain_plaza_'))
                    and name != 'Engineering_Fountain_Grand_Plaza_Arena']
    target.objects = source_names
for source_object in target.objects:
    if not source_object or source_object.type != 'MESH':
        continue
    copy = source_object.copy()
    copy.data = source_object.data.copy()
    copy.name = 'Cinematic_' + source_object.name
    scene.collection.objects.link(copy)
    copy.matrix_world = source_object.matrix_world.copy()
    copy.matrix_world.translation += Vector((-7.8042, -57.0706, 0))

# The source site contains explicit water sheets and spray meshes. Make render
# local copies of their materials so the narrow water curtains remain visible
# against the white pylons in this daylight render; the source asset is untouched.
water_material_overrides = {}
water_colors = {
    'Wabash_River_Water': (.035, .19, .28, 1),
    'Fountain_Aerated_Water_Stream': (.32, .69, .91, 1),
    'Fountain_Frothy_Water_Spray': (.77, .91, 1.0, 1),
}
for material_name, color in water_colors.items():
    source_material = bpy.data.materials.get(material_name)
    if not source_material:
        continue
    render_material = source_material.copy()
    render_material.name = 'Cinematic_' + material_name
    if render_material.use_nodes:
        for node in render_material.node_tree.nodes:
            if node.type != 'BSDF_PRINCIPLED':
                continue
            node.inputs['Base Color'].default_value = color
            node.inputs['Roughness'].default_value = .13 if 'Spray' not in material_name else .28
            if material_name in ('Wabash_River_Water', 'Fountain_Aerated_Water_Stream'):
                node.inputs['Alpha'].default_value = .84
            if 'Emission Color' in node.inputs:
                node.inputs['Emission Color'].default_value = (.025, .06, .085, 1)
            if 'Emission Strength' in node.inputs:
                node.inputs['Emission Strength'].default_value = {
                    'Wabash_River_Water': .12,
                    'Fountain_Aerated_Water_Stream': .16,
                    'Fountain_Frothy_Water_Spray': .14,
                }[material_name]
    water_material_overrides[material_name] = render_material

for obj in scene.objects:
    if obj.type != 'MESH' or not obj.name.startswith('Cinematic_'):
        continue
    for index, material in enumerate(obj.data.materials):
        if material and material.name in water_material_overrides:
            obj.data.materials[index] = water_material_overrides[material.name]


def make_day_sky():
    world = bpy.data.worlds.new('Cinematic Blue Hosek Wilkie Sky')
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()

    output = nodes.new('ShaderNodeOutputWorld')
    background = nodes.new('ShaderNodeBackground')
    sky = nodes.new('ShaderNodeTexSky')
    sky.sky_type = 'HOSEK_WILKIE'
    sky.sun_elevation = math.radians(42)
    sky.sun_rotation = math.radians(205)
    sky.sun_disc = True
    sky.sun_size = math.radians(.55)
    sky.sun_intensity = .75
    # Keep the horizon blue and legible instead of washing it into a gray band.
    sky.air_density = .42
    sky.ozone_density = 1.05

    coord = nodes.new('ShaderNodeTexCoord')
    cloud_noise = nodes.new('ShaderNodeTexNoise')
    # Sparse, high cloud wisps; broad high-contrast noise looked like fog blobs.
    cloud_noise.inputs['Scale'].default_value = 18.0
    cloud_noise.inputs['Detail'].default_value = 3.0
    cloud_noise.inputs['Roughness'].default_value = .72
    links.new(coord.outputs['Generated'], cloud_noise.inputs['Vector'])

    cloud_mask = nodes.new('ShaderNodeValToRGB')
    cloud_mask.color_ramp.elements[0].position = .70
    cloud_mask.color_ramp.elements[1].position = .81
    links.new(cloud_noise.outputs['Fac'], cloud_mask.inputs['Fac'])
    direction_z = nodes.new('ShaderNodeSeparateXYZ')
    links.new(coord.outputs['Generated'], direction_z.inputs['Vector'])

    # Keep the Hosek sky's atmospheric character, but blend it toward a clean
    # blue daylight gradient to avoid the gray horizontal haze in the renders.
    clear_sky = nodes.new('ShaderNodeValToRGB')
    ramp = clear_sky.color_ramp
    ramp.elements[0].position = 0.0
    ramp.elements[0].color = (.46, .68, .92, 1)
    ramp.elements[1].position = 1.0
    ramp.elements[1].color = (.11, .30, .70, 1)
    middle = ramp.elements.new(.34)
    middle.color = (.28, .51, .84, 1)
    links.new(direction_z.outputs['Z'], clear_sky.inputs['Fac'])
    sky_mix = nodes.new('ShaderNodeMixRGB')
    sky_mix.blend_type = 'MIX'
    sky_mix.inputs[0].default_value = .70
    links.new(sky.outputs['Color'], sky_mix.inputs[1])
    links.new(clear_sky.outputs['Color'], sky_mix.inputs[2])

    coverage = nodes.new('ShaderNodeMath')
    coverage.operation = 'MULTIPLY'
    links.new(cloud_mask.outputs['Color'], coverage.inputs[0])
    links.new(direction_z.outputs['Z'], coverage.inputs[1])

    cloud_tint = nodes.new('ShaderNodeMixRGB')
    cloud_tint.blend_type = 'MIX'
    cloud_tint.inputs[2].default_value = (.82, .87, .94, 1)
    links.new(coverage.outputs[0], cloud_tint.inputs[0])
    links.new(sky_mix.outputs['Color'], cloud_tint.inputs[1])
    links.new(cloud_tint.outputs['Color'], background.inputs['Color'])
    background.inputs['Strength'].default_value = .95
    links.new(background.outputs['Background'], output.inputs['Surface'])
    scene.world = world
    return world


make_day_sky()

# A broad midday sun gives clear shape; large neutral fills soften EEVEE shadows
# without creating the orange hotspots from the prior local area lights.
sun_data = bpy.data.lights.new('Soft Midday Sun', 'SUN')
sun_data.energy = 3.4
sun_data.color = (1.0, .95, .86)
sun_data.angle = math.radians(12)
sun_object = bpy.data.objects.new('Soft Midday Sun', sun_data)
scene.collection.objects.link(sun_object)
sun_direction = Vector((.30, .53, -.79)).normalized()
sun_object.rotation_euler = sun_direction.to_track_quat('-Z', 'Y').to_euler()


def add_area_fill(name, location, target, power, size, color=(.80, .87, 1.0)):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = power
    data.color = color
    data.shape = 'DISK'
    data.size = size
    data.use_shadow = False
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


add_area_fill('South Facade Sky Fill', (27, -58, 78), (10, 65, 0), 52000, 125)
add_area_fill('Fountain Plaza Sky Fill', (86, 150, 76), (-7, 138, 2), 46000, 115)
add_area_fill('WALC East Entrance Fill', (112, -8, 64), (30, -1, 8), 40000, 105)
add_area_fill('WALC Northwest Entrance Fill', (-65, 68, 66), (15, 0, 6), 42000, 115)
add_area_fill('Fountain Warm Water Accent', (18, 110, 35), (-7.8, 138, 5), 28000, 26,
              color=(1.0, .78, .58))
add_area_fill('Fountain Neutral Water Accent', (-45, 150, 32), (-7.8, 138, 5), 19000, 30,
              color=(1.0, .94, .82))


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


shots = [
    # Framed from the south-east, with the complete pylon form and its plaza visible.
    ('01_Engineering_Fountain', (15, 111, 7.0), (-7.8, 138, 5.0), 45),
    # A broad south-side campus view keeps the full WALC facade and approach in frame.
    ('02_WALC', (-70, 68, 15.0), (27, -1, 8.5), 28),
    # Pedestrian-height view directly on the northbound paved route toward the fountain.
    ('03_Road_between_WALC_and_Fountain', (-10, 105, 1.7), (-8.5, 138, 4.0), 32),
]

# Allow review passes to refresh only the road composition without re-rendering
# the other two cinematic frames. Normal runs still render all three shots.
if '--road-only' in sys.argv:
    shots = [shot for shot in shots if shot[0] == '03_Road_between_WALC_and_Fountain']

for name, position, target, lens in shots:
    camera_data = bpy.data.cameras.new(name)
    camera = bpy.data.objects.new(name, camera_data)
    scene.collection.objects.link(camera)
    camera.location = position
    aim(camera, target)
    camera_data.lens = lens
    camera_data.clip_start = .1
    camera_data.clip_end = 1200
    scene.camera = camera

    scene.render.engine = 'BLENDER_EEVEE'
    scene.eevee.taa_render_samples = 64
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.film_transparent = False
    scene.render.filepath = str(OUT / (name + '.png'))
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0
    bpy.ops.render.render(write_still=True)
    print('SAVED', name, scene.render.filepath)
