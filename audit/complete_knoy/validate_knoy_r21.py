import bpy, hashlib, json
from pathlib import Path

ROOT = Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
ASSET = ROOT / 'modular/buildings/knoy_hall.blend'
AUDIT = ROOT / 'audit/complete_knoy'
BASELINE = json.loads((AUDIT / 'r20_geometry_baseline_for_r21.json').read_text(encoding='utf-8'))
OUT = AUDIT / 'validation_round21.json'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))

def object_record(obj):
    rec = {
        'type': obj.type,
        'world': [[round(float(v), 7) for v in row] for row in obj.matrix_world],
    }
    if obj.type == 'MESH':
        rec['verts'] = [[round(float(c), 7) for c in v.co] for v in obj.data.vertices]
        rec['faces'] = [list(p.vertices) for p in obj.data.polygons]
    return rec

records = {obj.name: object_record(obj) for obj in bpy.data.objects}
digest = hashlib.sha256(json.dumps(records, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
basement = bpy.data.objects['KNOY_FloorSlab_Basement']
pts = [basement.matrix_world @ __import__('mathutils').Vector(v) for v in basement.bound_box]
basement_z = [min(p.z for p in pts), max(p.z for p in pts)]
assert len(bpy.data.objects) == BASELINE['scene_object_count']
assert sum(obj.type == 'MESH' for obj in bpy.data.objects) == BASELINE['mesh_object_count']
assert digest == BASELINE['all_object_mesh_and_world_matrix_sha256'], {
    'expected': BASELINE['all_object_mesh_and_world_matrix_sha256'], 'actual': digest
}
assert bpy.context.scene.get('knoy_r21_review_status', '').startswith('Added official 2019 emergency-plan')
assert all(term in basement.get('r21_source_check', '').lower() for term in ['upper-basement', 'lower-basement'])
assert 'ROUND 21' in bpy.data.texts['EVIDENCE_AND_INTERIOR_NOTES.txt'].as_string()
unpacked = [img.filepath for img in bpy.data.images if img.source == 'FILE' and img.filepath and not img.packed_file]
assert not unpacked

result = {
    'revision': 21,
    'passed': True,
    'reopened_saved_asset': True,
    'blender_version': bpy.app.version_string,
    'scene_object_count': len(bpy.data.objects),
    'mesh_object_count': sum(obj.type == 'MESH' for obj in bpy.data.objects),
    'r20_all_geometry_and_world_matrix_sha256': BASELINE['all_object_mesh_and_world_matrix_sha256'],
    'r21_all_geometry_and_world_matrix_sha256': digest,
    'all_mesh_geometry_and_object_world_transforms_unchanged': True,
    'basement_slab_local_world_z_bounds_m': [round(float(v), 3) for v in basement_z],
    'new_source_annotation_present': True,
    'unpacked_external_images': unpacked,
    'scope': 'Evidence-only R21 cross-check against Purdue 2019 Knoy emergency plan; no geometry, materials, object transforms, placement, or master edits.',
}
OUT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, indent=2))
