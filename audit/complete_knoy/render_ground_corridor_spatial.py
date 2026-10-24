"""Render a neutral, render-only eye-height corridor view for geometry review."""
import bpy
import json
from pathlib import Path
from mathutils import Vector

ROOT = Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
BLEND = ROOT / 'modular' / 'buildings' / 'knoy_hall.blend'
OUT = ROOT / 'audit' / 'complete_knoy' / 'knoy_l1_corridor_spatial_audit.png'
bpy.ops.wm.open_mainfile(filepath=str(BLEND))
scene = bpy.context.scene

kept_walls = {
    'KNOY_Ground_TracePartition_09', 'KNOY_Ground_TracePartition_09_AccessSide',
    'KNOY_Ground_TracePartition_11', 'KNOY_Ground_TracePartition_11_AccessSide',
    'KNOY_Ground_TracePartition_12', 'KNOY_Ground_TracePartition_12_AccessSide',
    'KNOY_Ground_TracePartition_13', 'KNOY_Ground_TracePartition_13_AccessSide',
}
kept_doors = {'KNOY_Illustrative_Door_11', 'KNOY_Illustrative_Door_12'}
for obj in scene.objects:
    obj.hide_render = obj.name not in kept_walls | kept_doors

# A temporary, matte floor patch gives the isolated passage segment spatial
# context. It is not the saved slab and makes no finish or as-built claim.
bpy.ops.mesh.primitive_plane_add(size=1, location=(1.05, -22.73, 0.14))
context_floor = bpy.context.object
context_floor.name = 'KNOY_Corridor_Audit_Temporary_Floor_Patch'
context_floor.scale = (7.88, 6.0, 1)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
context_floor.hide_render = False

def audit_material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = 0.9
    return mat

wall = audit_material('KNOY_Corridor_Audit_Wall_Neutral', (0.20, 0.26, 0.30))
door = audit_material('KNOY_Corridor_Audit_Door_Contrast', (0.82, 0.28, 0.06))
floor = audit_material('KNOY_Corridor_Audit_Floor_Neutral', (0.42, 0.45, 0.46))
for obj in scene.objects:
    if obj.type != 'MESH' or obj.hide_render:
        continue
    obj.data.materials.clear()
    obj.data.materials.append(door if obj.name.startswith('KNOY_Illustrative_Door_') else wall if obj.name in kept_walls else floor)

# The camera follows the passage segment and adjoining trace-defined open
# zones. Unrelated building geometry is hidden to make a longer section view.
camera_data = bpy.data.cameras.new('KNOY_Corridor_Spatial_Audit_Camera')
camera_data.lens = 38
camera = bpy.data.objects.new('KNOY_Corridor_Spatial_Audit_Camera', camera_data)
scene.collection.objects.link(camera)
camera.location = (12.0, -34.0, 9.0)
target = Vector((1.0, -22.7, 0.8))
camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
scene.camera = camera

# Camera-parented labels are a render overlay, not building signage.
label_mat = bpy.data.materials.new('KNOY_Corridor_Audit_Label_Overlay')
label_mat.diffuse_color = (0.025, 0.035, 0.045, 1)
label_mat.use_nodes = True
label_nodes = label_mat.node_tree.nodes
label_nodes.clear()
label_emission = label_nodes.new('ShaderNodeEmission')
label_emission.inputs['Color'].default_value = (0.025, 0.035, 0.045, 1)
label_emission.inputs['Strength'].default_value = 1
label_output = label_nodes.new('ShaderNodeOutputMaterial')
label_mat.node_tree.links.new(label_emission.outputs[0], label_output.inputs['Surface'])
for line, y, size in [
    ('KNOY L1  /  ILLUSTRATIVE SECTION CUTAWAY', 1.78, 0.15),
    ('GAPS 09/13 UNRESOLVED  •  NOT AS-BUILT OR ACCESSIBILITY REVIEW', 1.52, 0.105),
]:
    curve = bpy.data.curves.new('KNOY_Corridor_Audit_Label', 'FONT')
    curve.body = line
    curve.size = size
    curve.extrude = 0
    obj = bpy.data.objects.new('KNOY_Corridor_Audit_Label', curve)
    scene.collection.objects.link(obj)
    obj.parent = camera
    obj.location = (-3.1, y, -7.0)
    curve.materials.append(label_mat)

world = scene.world
world.use_nodes = True
background = world.node_tree.nodes.get('Background')
background.inputs['Color'].default_value = (0.75, 0.78, 0.8, 1)
background.inputs['Strength'].default_value = 0.65
for obj in list(scene.objects):
    if obj.type == 'LIGHT':
        obj.hide_render = True
for name, location, energy, size in [
    ('KNOY_Corridor_Audit_Key', (8.0, -31.0, 11.0), 2600, 7.0),
    ('KNOY_Corridor_Audit_Fill', (-7.0, -18.0, 7.0), 1600, 9.0),
]:
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = energy
    data.shape = 'DISK'
    data.size = size
    light = bpy.data.objects.new(name, data)
    scene.collection.objects.link(light)
    light.location = location
    light.rotation_euler = (Vector((1.0, -22.7, 1.0)) - light.location).to_track_quat('-Z', 'Y').to_euler()

scene.render.engine = 'CYCLES'
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_x = 1800
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
scene.render.filepath = str(OUT)
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'Medium High Contrast'
bpy.ops.render.render(write_still=True)

audit = {
    'source_asset': str(BLEND.relative_to(ROOT)),
    'render': str(OUT.relative_to(ROOT)),
    'camera': {'location_m': list(camera.location), 'look_target_m': list(target), 'lens_mm': camera_data.lens, 'status': 'Illustrative eye-height view; camera is not a surveyed location.'},
    'view_height': 'Eye-height camera at 1.62 m with elevated oblique framing; shows modeled wall/leaf height and adjoining open zones, not a clearance check.',
    'temporary_materials': 'Dark neutral walls, orange door leaves, and gray floor are render-only high-contrast coding; no actual interior finish or color is claimed.',
    'modeled_geometry': 'Render isolates traced wall segments 09/11/12/13 and their access-side components, with illustrative leaves 11/12. The longer section shows their modeled spatial connections; unrelated walls are hidden. Wall height, thickness, and leaf dimensions are estimates.',
    'unresolved_openings': 'Candidate gaps 09 and 13 occur in the displayed trace but remain unresolved; they are left without leaf geometry and are not confirmed paths. Candidate gaps 17/18/20/24 elsewhere remain unresolved.',
    'not_verified': 'This is not an as-built corridor survey. The 1984-era thesis raster trace is manually registered and uncertain; the view and temporary floor patch do not establish a complete route, door positions, code/accessibility clearance, finishes, furnishings, or certified landings.',
}
(OUT.parent / 'corridor_spatial_audit.json').write_text(json.dumps(audit, indent=2) + '\n', encoding='utf-8')
print(json.dumps(audit, indent=2))
