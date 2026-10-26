from pathlib import Path
from mathutils import Vector
import bpy, hashlib, json, os

root = Path(bpy.path.abspath('//'))
manifest = json.loads((root/'modular/manifest.json').read_text(encoding='utf-8'))
assets = {a['id']: a for a in manifest['assets']}
ids = [
    'massing_fairway_cooperative_2101b77',
    'massing_faith_west_community_center_84aa829',
    'massing_family_express_a07e1fb',
    'massing_farmhouse_fraternity_purdue_chapter_0b8908b',
    'massing_first_street_towers_central_fstc_929924d',
    'massing_first_street_towers_east_fste_c9b22d3',
    'massing_first_street_towers_west_fstw_b6c3bbe',
    'massing_forney_hall_of_chemical_engineering_frny_d94ba3a',
]

def norm(path):
    return os.path.normcase(os.path.abspath(bpy.path.abspath(path)))

def bounds(collection):
    coords = []
    for obj in collection.all_objects:
        if obj.type not in {'MESH', 'FONT', 'CURVE', 'SURFACE', 'META'}:
            continue
        coords.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    if not coords:
        raise AssertionError(f'No bounded objects in {collection.name}')
    return [[min(v[i] for v in coords), max(v[i] for v in coords)] for i in range(3)]

assert Path(bpy.data.filepath).name == 'purdue_campus_master.blend'
rows = {}
problems = []
for asset_id in ids:
    asset = assets[asset_id]
    collection = bpy.data.collections.get(asset['collection'])
    if not collection:
        problems.append(f'{asset_id}: collection missing')
        continue
    expected_path = norm(str(root/'modular'/asset['file']))
    if not collection.library or norm(collection.library.filepath) != expected_path:
        problems.append(f'{asset_id}: linked library path mismatch')
    objects = list(collection.all_objects)
    actual_bounds = bounds(collection)
    if len(objects) != asset['object_count']:
        problems.append(f'{asset_id}: expected {asset["object_count"]} objects, got {len(objects)}')
    for axis in range(3):
        for side in range(2):
            if abs(actual_bounds[axis][side] - asset['bounds_world_m'][axis][side]) > 0.03:
                problems.append(f'{asset_id}: bounds mismatch on axis {axis}, side {side}')
    linked = [obj for obj in bpy.context.scene.objects if obj.library and norm(obj.library.filepath) == expected_path]
    if len(linked) != asset['object_count']:
        problems.append(f'{asset_id}: expected {asset["object_count"]} scene links, got {len(linked)}')
    if len([c for c in bpy.data.collections if c.name == asset['collection']]) != 1:
        problems.append(f'{asset_id}: duplicate or missing named collection')
    rows[asset_id] = {
        'collection': collection.name,
        'library': collection.library.filepath if collection.library else None,
        'objects': len(objects),
        'scene_linked_objects': len(linked),
        'bounds_world_m': actual_bounds,
        'expected_bounds_world_m': asset['bounds_world_m'],
        'sha256': hashlib.sha256((root/'modular'/asset['file']).read_bytes()).hexdigest(),
    }

libraries = [{'path': lib.filepath, 'exists': Path(bpy.path.abspath(lib.filepath)).exists()} for lib in bpy.data.libraries]
missing = [lib for lib in libraries if not lib['exists']]
if missing:
    problems.append(f'{len(missing)} linked libraries are missing')
report = {
    'status': 'PASS' if not problems else 'FAIL',
    'master': str(Path(bpy.data.filepath)),
    'blender_version': bpy.app.version_string,
    'scene_object_count': len(bpy.context.scene.objects),
    'library_count': len(libraries),
    'missing_library_count': len(missing),
    'assets': rows,
    'problems': problems,
}
(root/'audit/master_verify_eight_graded.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
print('MASTER_VERIFY_EIGHT', json.dumps({
    'status': report['status'],
    'scene_objects': report['scene_object_count'],
    'libraries': len(libraries),
    'missing': len(missing),
    'asset_objects': {key: value['objects'] for key, value in rows.items()},
    'problems': problems,
}))
if problems:
    raise RuntimeError('; '.join(problems))
