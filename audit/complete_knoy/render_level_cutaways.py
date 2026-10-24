"""Render comparable, non-destructive Knoy interior cutaway evidence views."""
import bpy
import bmesh
import json
from pathlib import Path
from mathutils import Vector

ROOT = Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
BLEND = ROOT / 'modular' / 'buildings' / 'knoy_hall.blend'
OUT_DIR = ROOT / 'audit' / 'complete_knoy'
bpy.ops.wm.open_mainfile(filepath=str(BLEND))
scene = bpy.context.scene


def material(name, rgba, roughness=0.88):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = rgba
    mat.use_nodes = True
    # An emission component keeps thin traced walls readable at plan scale and
    # avoids changes in apparent color caused by the temporary audit lighting.
    bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value = rgba
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Emission Color'].default_value = rgba
    bsdf.inputs['Emission Strength'].default_value = 0.45
    return mat


# Neutral contrast is strictly render-only. The building file is never saved here.
wall_mat = material('KNOY_Cutaway_Audit_Wall', (0.018, 0.055, 0.085, 1))
floor_mat = material('KNOY_Cutaway_Audit_Floor', (0.19, 0.23, 0.26, 1))
door_mat = material('KNOY_Cutaway_Audit_Door_Estimate', (0.95, 0.20, 0.012, 1))
stair_mat = material('KNOY_Cutaway_Audit_Stair_Estimate', (0.9, 0.48, 0.015, 1))

world = scene.world
world.use_nodes = True
world.node_tree.nodes.get('Background').inputs['Color'].default_value = (1, 1, 1, 1)
world.node_tree.nodes.get('Background').inputs['Strength'].default_value = 1

for obj in scene.objects:
    obj.hide_render = True

# Reuse one camera, sunlight-like area fill, and gentle soft fill for every floor.
camera_data = bpy.data.cameras.new('KNOY_Level_Cutaway_Audit_Camera')
camera = bpy.data.objects.new('KNOY_Level_Cutaway_Audit_Camera', camera_data)
scene.collection.objects.link(camera)
camera_data.type = 'ORTHO'
camera_data.ortho_scale = 92
camera.location = (0, 0, 140)
camera.rotation_euler = (Vector((0, 0, 0)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
scene.camera = camera

key_data = bpy.data.lights.new('KNOY_Cutaway_Audit_Key', 'AREA')
key_data.energy = 15000
key_data.shape = 'DISK'
key_data.size = 34
key = bpy.data.objects.new('KNOY_Cutaway_Audit_Key', key_data)
scene.collection.objects.link(key)
key.location = (28, -42, 78)
key.rotation_euler = (Vector((0, 0, 0)) - key.location).to_track_quat('-Z', 'Y').to_euler()

fill_data = bpy.data.lights.new('KNOY_Cutaway_Audit_Fill', 'AREA')
fill_data.energy = 8000
fill_data.shape = 'DISK'
fill_data.size = 42
fill = bpy.data.objects.new('KNOY_Cutaway_Audit_Fill', fill_data)
scene.collection.objects.link(fill)
fill.location = (-35, 18, 62)
fill.rotation_euler = (Vector((0, 0, 0)) - fill.location).to_track_quat('-Z', 'Y').to_euler()


def set_top_cut(obj, cut_z):
    """Uniformly shorten a render-only copy about its bottom plane."""
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    bottom = min(v.z for v in corners)
    top = max(v.z for v in corners)
    if top <= bottom or cut_z >= top:
        return 1.0
    ratio = max(0.03, min(1.0, (cut_z - bottom) / (top - bottom)))
    old_location = obj.location.z
    obj.scale.z *= ratio
    obj.location.z = bottom - ratio * (bottom - old_location)
    return ratio


floor_configs = [
    {'level': 'L1', 'floor': 'KNOY_FloorSlab_L1_Ground', 'partition_prefix': 'KNOY_Ground_TracePartition_', 'z': 0.15, 'stair_prefixes': []},
    {'level': 'L2', 'floor': 'KNOY_FloorSlab_L2', 'partition_prefix': 'KNOY_L2_TypicalPlan_InteriorPartitions', 'z': 4.481, 'stair_prefixes': ['KNOY_Stair_L2_L3_']},
    {'level': 'L3', 'floor': 'KNOY_FloorSlab_L3', 'partition_prefix': 'KNOY_L3_TypicalPlan_InteriorPartitions', 'z': 8.961, 'stair_prefixes': ['KNOY_Stair_L3_L4_']},
    {'level': 'L4', 'floor': 'KNOY_FloorSlab_L4', 'partition_prefix': 'KNOY_L4_TypicalPlan_InteriorPartitions', 'z': 13.442, 'stair_prefixes': ['KNOY_Stair_L3_L4_']},
]

summary = {
    'asset': str(BLEND),
    'method': 'Render-only horizontal section at floor elevation + 1.45 m, presented as a top-down orthographic cutaway so the plan-traced partitions remain readable. Floor slabs are omitted to prevent obscuring the traced partition and stair meshes. Source blend is opened, not saved. L2-L4 share the same camera and scale.',
    'source_finish_status': 'Near-black blue walls, orange door leaves, amber stairs, and white background are temporary high-contrast audit coding; they are not actual finishes. No verified interior finish schedule or interior photograph supports actual colors.',
    'unresolved_door_status': 'Ground level has 12 illustrative leaves. Six candidate gaps 09, 13, 17, 18, 20, 24 remain unresolved; no candidate leaves are invented in this render. See door_gap_collision_audit.json.',
    'levels': [],
}

scene.render.engine = 'CYCLES'
scene.cycles.samples = 8
scene.cycles.use_denoising = True
scene.render.resolution_x = 2200
scene.render.resolution_y = 3300
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.view_settings.view_transform = 'Standard'

for config in floor_configs:
    level = config['level']
    floor = bpy.data.objects.get(config['floor'])
    if floor is None:
        raise RuntimeError(f'Missing source slab: {config["floor"]}')
    # Hide slabs in this audit view: floor meshes have irregular cut-outs whose
    # underside shading obscures the interior trace; a plan-like cutaway keeps
    # the evidence walls and stair runs visually readable.
    floor.hide_render = True
    if floor.type == 'MESH':
        floor.data.materials.clear()
        floor.data.materials.append(floor_mat)
        for polygon in floor.data.polygons:
            polygon.material_index = 0
        bm = bmesh.new()
        bm.from_mesh(floor.data)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(floor.data)
        bm.free()

    wall_names = []
    for obj in scene.objects:
        if obj.type != 'MESH':
            continue
        is_wall = obj.name.startswith(config['partition_prefix'])
        is_door = level == 'L1' and obj.name.startswith('KNOY_Illustrative_Door_')
        is_stair = any(obj.name.startswith(prefix) for prefix in config['stair_prefixes'])
        if is_wall or is_door or is_stair:
            obj.hide_render = False
            if is_wall:
                obj.data.materials.clear()
                obj.data.materials.append(wall_mat)
                set_top_cut(obj, config['z'] + 1.45)
                wall_names.append(obj.name)
            elif is_door:
                obj.data.materials.clear()
                obj.data.materials.append(door_mat)
                set_top_cut(obj, config['z'] + 1.45)
            elif is_stair:
                obj.data.materials.clear()
                obj.data.materials.append(stair_mat)

    output = OUT_DIR / f'knoy_{level.lower()}_interior_cutaway.png'
    scene.render.filepath = str(output)
    bpy.ops.render.render(write_still=True)
    summary['levels'].append({
        'level': level,
        'floor_slab': config['floor'],
        'floor_slab_visible': False,
        'partition_objects': wall_names,
        'render': str(output.relative_to(ROOT)),
        'cut_height_above_floor_m': 1.45,
        'stairs_visible': [o.name for o in scene.objects if o.type == 'MESH' and not o.hide_render and any(o.name.startswith(p) for p in config['stair_prefixes'])],
    })
    floor.hide_render = True
    for obj in scene.objects:
        if obj.type == 'MESH' and (obj.name.startswith(config['partition_prefix']) or (level == 'L1' and obj.name.startswith('KNOY_Illustrative_Door_')) or any(obj.name.startswith(p) for p in config['stair_prefixes'])):
            obj.hide_render = True

# A closer top-down L1 plan crop makes the illustrative leaves and their wall
# gaps legible. This is still a render-only audit framing, not a measured plan.
for obj in scene.objects:
    if obj.type == 'MESH' and (obj.name.startswith('KNOY_Ground_TracePartition_') or obj.name.startswith('KNOY_Illustrative_Door_')):
        obj.hide_render = True
for obj in scene.objects:
    if obj.type == 'MESH' and (obj.name.startswith('KNOY_Ground_TracePartition_') or obj.name.startswith('KNOY_Illustrative_Door_')):
        obj.hide_render = False
camera_data.ortho_scale = 60
camera.location = (0, 0, 95)
camera.rotation_euler = (Vector((0, -5, 0.15)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
scene.render.resolution_x = 2800
scene.render.resolution_y = 2100
detail_out = OUT_DIR / 'knoy_l1_door_corridor_cutaway.png'
scene.render.filepath = str(detail_out)
bpy.ops.render.render(write_still=True)
summary['ground_interior_detail_render'] = str(detail_out.relative_to(ROOT))

(OUT_DIR / 'interior_cutaway_render_audit.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
print(json.dumps(summary, indent=2))
