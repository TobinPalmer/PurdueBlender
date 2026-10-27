import hashlib
import json
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(bpy.data.filepath).resolve().parent
MANIFEST = json.loads((ROOT / 'modular' / 'manifest.json').read_text(encoding='utf-8'))
ASSET_IDS = ['dauch_alumni_center', 'electrical_engineering', 'flex_lab', 'frieda_parker_hall', 'hansen_life_sciences', 'hicks_library', 'massing_west_lafayette_intermediate_school_d72f0fa']
records = {a['id']: a for a in MANIFEST['assets']}
scene = bpy.context.scene
errors = []
results = []

def local_matrix(obj, cache):
    if obj in cache:
        return cache[obj]
    matrix = obj.matrix_local.copy()
    if obj.parent is not None:
        matrix = local_matrix(obj.parent, cache) @ matrix
    cache[obj] = matrix
    return matrix

for asset_id in ASSET_IDS:
    record = records.get(asset_id)
    if record is None:
        errors.append(f'{asset_id}: missing from manifest')
        continue
    asset_path = (ROOT / 'modular' / record['file']).resolve()
    if not asset_path.is_file():
        errors.append(f'{asset_id}: missing library {asset_path}')
        continue
    actual_sha = hashlib.sha256(asset_path.read_bytes()).hexdigest()
    if actual_sha != record.get('sha256'):
        errors.append(f'{asset_id}: SHA mismatch {actual_sha} != {record.get("sha256")}')
    collection = bpy.data.collections.get(record['collection'])
    if collection is None:
        errors.append(f'{asset_id}: linked collection missing')
        continue
    linked_path = Path(bpy.path.abspath(collection.library.filepath)).resolve() if collection.library else None
    if linked_path != asset_path:
        errors.append(f'{asset_id}: linked path {linked_path} != {asset_path}')
    objects = list(collection.all_objects)
    if len(objects) != record.get('object_count'):
        errors.append(f'{asset_id}: object count {len(objects)} != manifest {record.get("object_count")}')
    points = []
    if record.get('kind') == 'detailed':
        marker = bpy.data.objects.get('Placement_' + asset_id)
        if marker is None or marker.instance_collection != collection:
            errors.append(f'{asset_id}: correct placement marker/collection instance missing')
            marker_xy = None
        else:
            marker_xy = [float(marker.location.x), float(marker.location.y)]
            origin = record.get('placement_origin_xy_m')
            if not origin or max(abs(marker_xy[i] - origin[i]) for i in range(2)) > 0.001:
                errors.append(f'{asset_id}: marker placement mismatch {marker_xy} != {origin}')
        cache = {}
        for obj in objects:
            if obj.type != 'MESH':
                continue
            mat = local_matrix(obj, cache)
            for corner in obj.bound_box:
                point = mat @ Vector(corner)
                if marker_xy is not None:
                    point.x += marker_xy[0]
                    point.y += marker_xy[1]
                points.append(point)
        placement_mode = 'collection instance through Placement marker'
    else:
        direct_links = sum(child == collection for child in scene.collection.children)
        if direct_links != 1:
            errors.append(f'{asset_id}: expected one direct collection link, got {direct_links}')
        for obj in objects:
            if obj.type == 'MESH':
                points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
        marker_xy = None
        placement_mode = 'direct campus-coordinate collection link'
    bounds = [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)] if points else None
    expected_bounds = record.get('bounds_world_m')
    max_error = max(abs(bounds[i][j] - expected_bounds[i][j]) for i in range(3) for j in range(2)) if bounds and expected_bounds else None
    if max_error is None or max_error > 0.01:
        errors.append(f'{asset_id}: manifest world-bound error {max_error}')
    results.append({
        'id': asset_id,
        'score': record.get('independent_grade_score'),
        'sha256': actual_sha,
        'linked_collection': collection.name,
        'library_path': str(linked_path) if linked_path else None,
        'placement_mode': placement_mode,
        'placement_xy_m': marker_xy,
        'object_count': len(objects),
        'mesh_object_count': sum(obj.type == 'MESH' for obj in objects),
        'bounds_world_m': bounds,
        'max_manifest_bounds_error_m': max_error,
        'accuracy_status': record.get('accuracy_status'),
    })

report = {
    'status': 'PASS' if not errors else 'FAIL',
    'master_file': str(Path(bpy.data.filepath).resolve()),
    'fresh_open_blender_version': bpy.app.version_string,
    'scene': scene.name,
    'scene_object_count': len(scene.objects),
    'checked_buildings': len(results),
    'results': results,
    'errors': errors,
}
out = ROOT / 'audit' / 'master_integration_2026-10-27_r5.json'
out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(json.dumps(report, indent=2, ensure_ascii=False))
if errors:
    raise RuntimeError('Master integration verification failed: ' + '; '.join(errors))
