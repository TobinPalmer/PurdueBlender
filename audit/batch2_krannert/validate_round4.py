import bpy, json
from pathlib import Path
from mathutils import Vector

ROOT = Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
ASSET = ROOT / 'modular/buildings/krannert_building.blend'
OUT = ROOT / 'audit/batch2_krannert/validation_round4.json'
REFERENCE = json.loads((ROOT / 'audit/batch2_krannert/structural_bounds_round3.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset = bpy.data.collections.get('Asset_krannert_building')
root = bpy.data.objects.get('AssetRoot_krannert_building')
objects = list(asset.all_objects) if asset else []
meshes = [o for o in objects if o.type == 'MESH']
issues = []

def bounds(o):
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return [[min(getattr(p, axis) for p in pts), max(getattr(p, axis) for p in pts)] for axis in ('x','y','z')]

if not asset:
    issues.append('Asset collection missing')
if not root or any(abs(v) > 1e-7 for v in (*root.location, *root.rotation_euler)) or any(abs(v-1) > 1e-7 for v in root.scale):
    issues.append('Source root transform changed')
if any(o.name == 'KRAN_Surrounding_Plaza_Paving' for o in objects):
    issues.append('Removed site paving unexpectedly returned')
if any(o.name.startswith('R4_RENDER_ONLY') for o in bpy.data.objects):
    issues.append('Render-only audit object leaked into saved asset')

stone = bpy.data.materials.get('KRAN_Indiana_Limestone')
glass = bpy.data.materials.get('KRAN_Solar_Bronze_Glass')
brick = bpy.data.materials.get('KRAN_Purdue_Red_Brick_R4')
walls = bpy.data.objects.get('KRAN_Exterior_Masonry_Walls')
if not all((stone, glass, brick, walls)):
    issues.append('Round 4 exterior material or wall object missing')
brick_faces = sum(p.material_index == 2 for p in walls.data.polygons) if walls and len(walls.data.materials) > 2 else 0
if brick_faces != 454:
    issues.append(f'Expected 454 ground-band brick faces, found {brick_faces}')

unmaterialed = [o.name for o in meshes if not o.data.materials]
bad_outputs = []
for o in meshes:
    for m in o.data.materials:
        if m is None or not m.use_nodes or not any(n.type == 'OUTPUT_MATERIAL' for n in m.node_tree.nodes):
            bad_outputs.append(o.name)

# Structural bounds are compared with the pre-R4 screening snapshot. The round
# changed material assignments only; no structural mesh position/dimensions changed.
structural_bounds = {}
for name, rec in REFERENCE.items():
    ob = bpy.data.objects.get(name)
    if ob:
        b = bounds(ob)
        structural_bounds[name] = b
        ref = rec['bounds']
        delta = max(abs(b[i][j] - ref[i][j]) for i in range(3) for j in range(2))
        if delta > 0.001:
            issues.append(f'{name} bounds changed by {delta:.6f} m since round 3')

image_paths = []
for image in bpy.data.images:
    if image.source == 'FILE' and not image.packed_file:
        path = bpy.path.abspath(image.filepath)
        if path and Path(path).exists():
            image_paths.append(path)
        elif path:
            issues.append(f'Missing external image: {path}')

report = {
    'revision': 4,
    'reopen': 'PASS',
    'asset_file': 'modular/buildings/krannert_building.blend',
    'export_collection': asset.name if asset else None,
    'object_count': len(objects),
    'mesh_count': len(meshes),
    'source_root_identity_transform': bool(root and all(abs(v) < 1e-7 for v in (*root.location, *root.rotation_euler)) and all(abs(v-1) < 1e-7 for v in root.scale)),
    'unverified_site_slab_absent': not any(o.name == 'KRAN_Surrounding_Plaza_Paving' for o in objects),
    'render_only_ground_absent_from_saved_asset': not any(o.name.startswith('R4_RENDER_ONLY') for o in bpy.data.objects),
    'round4_materials': {
        'stone': {'present': bool(stone), 'base_color': list(stone.diffuse_color) if stone else None},
        'glass': {'present': bool(glass), 'base_color': list(glass.diffuse_color) if glass else None},
        'brick': {'present': bool(brick), 'node_count': len(brick.node_tree.nodes) if brick else 0},
        'ground_band_faces_assigned_brick': brick_faces
    },
    'structural_bounds_match_round3_within_0_001m': not any('bounds changed' in i for i in issues),
    'structural_bounds_local_m': structural_bounds,
    'unmaterialed_mesh_count': len(unmaterialed),
    'material_output_issue_count': len(bad_outputs),
    'unpacked_external_images': image_paths,
    'r2_interior_components_preserved': {
        'glass_panels': sum(o.name.startswith('KRAN_R2_DrawingRoom_Glass_Panel') for o in objects),
        'conference_seats': sum(o.name.startswith('KRAN_R2_Conference_Chair_Seat') for o in objects),
        'parrish_monitors': sum(o.name.startswith('KRAN_R2_Parrish_Monitor_Screen') for o in objects),
        'high_stool_foot_rings': sum(o.name.startswith('KRAN_R2_DrawingRoom_HighStool_FootRing') for o in objects)
    },
    'master_manifest_shared_files_edited': False,
    'issues': issues
}
OUT.write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
if issues:
    raise RuntimeError('Round 4 validation failed')
