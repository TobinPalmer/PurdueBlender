import bpy
import json
import math
import os
from math import cos, radians

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
ASSET_PATH = os.path.join(REPO, 'modular', 'buildings', 'asian_american_resource_and_cultural_center.blend')
GIS_PATH = os.path.join(HERE, 'sources', 'aaarcc_gis_feature_926.json')
MANIFEST_PATH = os.path.join(REPO, 'modular', 'manifest.json')
PROBE_PATH = os.path.join(HERE, 'aaarcc_collection_export_probe.blend')
OUT_PATH = os.path.join(HERE, 'reopen_verification.json')

EXPECTED_ID = 'asian_american_resource_and_cultural_center'
EXPECTED_COLLECTION = 'Asset_asian_american_resource_and_cultural_center'
EXPECTED_SCENE = 'Building_asian_american_resource_and_cultural_center'

with open(MANIFEST_PATH, encoding='utf-8') as f:
    manifest = json.load(f)
entry = next(x for x in manifest['assets'] if x['id'] == EXPECTED_ID)
assert entry['file'] == 'buildings/asian_american_resource_and_cultural_center.blend'
assert entry['collection'] == EXPECTED_COLLECTION
assert entry['scene'] == EXPECTED_SCENE
assert entry['local_coordinates'] is True

bpy.ops.wm.open_mainfile(filepath=ASSET_PATH)
scene = bpy.context.scene
asset = bpy.data.collections.get(EXPECTED_COLLECTION)
assert scene.name == EXPECTED_SCENE, scene.name
assert asset is not None
actual_count = len(asset.objects)
assert not any(o.type in {'CAMERA', 'LIGHT'} for o in asset.objects)
assert bpy.data.collections.get('Preview_only') is not None
preview = bpy.data.collections['Preview_only']
assert any(o.type == 'CAMERA' for o in preview.objects)
assert any(o.type == 'LIGHT' for o in preview.objects)

# Verify the exact official source ring against the plinth mesh in local project coordinates.
with open(GIS_PATH, encoding='utf-8') as f:
    payload = json.load(f)
feature = payload[0] if isinstance(payload, list) else payload
ring_ll = feature['geometry']['rings'][0]
lon_scale = 111412.84 * cos(radians(40.4274))
lat_scale = 111040.0
origin_lon, origin_lat = -86.9137, 40.4274
pts_xy = [((p[0] - origin_lon) * lon_scale, (p[1] - origin_lat) * lat_scale) for p in ring_ll]
minx, maxx = min(p[0] for p in pts_xy), max(p[0] for p in pts_xy)
miny, maxy = min(p[1] for p in pts_xy), max(p[1] for p in pts_xy)
center = ((minx + maxx) / 2, (miny + maxy) / 2)
ring_local = [(x - center[0], y - center[1]) for x, y in pts_xy]
plinth = bpy.data.objects.get('AAARCC exact GIS perimeter | stone plinth')
assert plinth is not None and plinth.type == 'MESH'
source_xy = ring_local[:-1] if ring_local[0] == ring_local[-1] else ring_local
model_xy = [(v.co.x, v.co.y) for v in plinth.data.vertices[:len(source_xy)]]
assert len(source_xy) == len(model_xy), (len(source_xy), len(model_xy))
source_to_model = max(min(math.dist(a, b) for b in model_xy) for a in source_xy)
model_to_source = max(min(math.dist(b, a) for a in source_xy) for b in model_xy)
max_vertex_error = max(source_to_model, model_to_source)

mesh_objects = [o for o in asset.objects if o.type == 'MESH']
font_objects = [o for o in asset.objects if o.type == 'FONT']
deps = []
for img in bpy.data.images:
    if img.source == 'FILE' and img.filepath:
        resolved = bpy.path.abspath(img.filepath)
        if os.path.isabs(resolved) and not resolved.startswith(os.path.abspath(REPO)):
            deps.append(resolved)
assert not deps, deps

world_points = []
for obj in mesh_objects:
    for corner in obj.bound_box:
        world_points.append(obj.matrix_world @ bpy.mathutils.Vector(corner) if hasattr(bpy, 'mathutils') else obj.matrix_world @ __import__('mathutils').Vector(corner))
bounds = [[min(p[i] for p in world_points), max(p[i] for p in world_points)] for i in range(3)]
assert max_vertex_error < 1e-5, max_vertex_error
assert len(mesh_objects) == 432 and len(font_objects) == 1
assert abs(bounds[2][1] - 10.05) < 1e-4

# A collection-only library write checks that the export contract is self-contained.
bpy.data.libraries.write(PROBE_PATH, {asset}, fake_user=True, compress=True)
result = {
    'status': 'PASS',
    'reopened_asset': os.path.relpath(ASSET_PATH, REPO).replace('\\', '/'),
    'asset_id': EXPECTED_ID,
    'scene': scene.name,
    'collection': asset.name,
    'manifest_collection_object_count_before_coordinator_refresh': entry['object_count'],
    'reopened_collection_object_count': actual_count,
    'manifest_count_refresh_required': entry['object_count'] != actual_count,
    'mesh_object_count': len(mesh_objects),
    'font_object_count': len(font_objects),
    'camera_or_light_in_export': False,
    'preview_helpers_in_sibling_collection': True,
    'GIS_feature_id': feature.get('attributes', {}).get('FID'),
    'GIS_ring_vertex_count_excluding_closure': len(source_xy),
    'GIS_plinth_vertex_count_checked': len(model_xy),
    'max_symmetric_nearest_vertex_error_m': max_vertex_error,
    'placement_origin_xy_m': entry['placement_origin_xy_m'],
    'evaluated_mesh_bounds_local_m': bounds,
    'external_image_dependencies': deps,
    'collection_export_probe': os.path.basename(PROBE_PATH),
    'height_status': 'estimated from photos; no surveyed elevations located',
    'roof_status': 'pitched gable form supported by official exterior photos; exact geometry/height unverified',
    'verification_date': '2026-10-25'
}
with open(OUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2)
print(json.dumps(result, indent=2))
