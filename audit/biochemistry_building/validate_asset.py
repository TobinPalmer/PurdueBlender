"""Reopen and collection-only import checks for the Biochemistry library."""
import bpy
import json
import math
import os
from mathutils import Vector

audit_dir = os.path.dirname(os.path.abspath(__file__))
repo = os.path.abspath(os.path.join(audit_dir, '..', '..'))
asset_path = os.path.join(repo, 'modular', 'buildings', 'biochemistry_building.blend')
gis_path = os.path.join(audit_dir, 'sources', 'biochemistry_building_gis_fid238_2026-10-25.json')
manifest_path = os.path.join(repo, 'modular', 'manifest.json')
result_path = os.path.join(audit_dir, 'reopen_validation.json')
asset_id = 'biochemistry_building'
collection_name = 'Asset_biochemistry_building'

# The validator is launched with the saved library already opened in background Blender.
scene = bpy.context.scene
asset_col = bpy.data.collections.get(collection_name)
assert scene.name == 'Scene'
assert asset_col is not None
assert asset_col.name == collection_name
assert len(asset_col.objects) > 0
assert all(obj.type not in {'CAMERA', 'LIGHT'} for obj in asset_col.objects)
assert all(obj.parent is None for obj in asset_col.objects)
reopened_object_count = len(asset_col.objects)
reopened_mesh_count = sum(obj.type == 'MESH' for obj in asset_col.objects)
reopened_font_count = sum(obj.type == 'FONT' for obj in asset_col.objects)

with open(manifest_path, encoding='utf-8') as f:
    manifest = json.load(f)
entry = next(item for item in manifest['assets'] if item['id'] == asset_id)
assert entry['file'] == 'buildings/biochemistry_building.blend'
assert entry['collection'] == collection_name
assert entry['scene'] == 'Scene'
assert entry['local_coordinates'] is True

with open(gis_path, encoding='utf-8') as f:
    feature = json.load(f)['features'][0]
ring_ll = feature['geometry']['rings'][0]
lat0, lon0 = 40.4274, -86.9137
lon_scale = 111412.84 * math.cos(math.radians(lat0))
gis_xy = [((lon - lon0) * lon_scale, (lat - lat0) * 111040.0) for lon, lat in ring_ll[:-1]]
cross = [gis_xy[i][0] * gis_xy[(i + 1) % len(gis_xy)][1] - gis_xy[(i + 1) % len(gis_xy)][0] * gis_xy[i][1] for i in range(len(gis_xy))]
area2 = sum(cross)
origin_x = sum((gis_xy[i][0] + gis_xy[(i + 1) % len(gis_xy)][0]) * cross[i] for i in range(len(gis_xy))) / (3 * area2)
origin_y = sum((gis_xy[i][1] + gis_xy[(i + 1) % len(gis_xy)][1]) * cross[i] for i in range(len(gis_xy))) / (3 * area2)
expected_origin = entry['placement_origin_xy_m']
origin_error = math.dist((origin_x, origin_y), expected_origin)
assert origin_error < 1e-6
gis_local = [(x - origin_x, y - origin_y) for x, y in gis_xy]

def point_in_ring(point):
    x, y = point
    inside = False
    for i, (x1, y1) in enumerate(gis_local):
        x2, y2 = gis_local[(i + 1) % len(gis_local)]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            inside = not inside
    return inside

shell = bpy.data.objects.get('biochemistry_building_GIS_outline_primary_shell')
assert shell is not None and shell.type == 'MESH'
shell_xy = [(shell.matrix_world @ v.co).xy for v in shell.data.vertices[:len(gis_local)]]
shell_vertices = [(float(v.x), float(v.y)) for v in shell_xy]
vertex_errors = [min(math.dist(p, q) for q in shell_vertices) for p in gis_local]
max_vertex_error = max(vertex_errors)
assert max_vertex_error < 1e-5, max_vertex_error

world_points = []
for obj in asset_col.objects:
    if obj.type != 'MESH':
        continue
    world_points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
bounds = [[min(p[i] for p in world_points), max(p[i] for p in world_points)] for i in range(3)]
roof_equipment = []
for obj in asset_col.objects:
    if not any(tag in obj.name for tag in ('rooftop mechanical screen', 'roof exhaust stack')):
        continue
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    center = (sum(p.x for p in corners) / 8, sum(p.y for p in corners) / 8)
    assert point_in_ring(center), (obj.name, center)
    roof_equipment.append({'name': obj.name, 'center_xy_m': list(center), 'center_inside_gis_ring': True})

external_image_paths = [img.filepath for img in bpy.data.images if img.source != 'GENERATED' and img.filepath]
linked_library_paths = [lib.filepath for lib in bpy.data.libraries if lib.filepath]
assert not external_image_paths, external_image_paths
assert not linked_library_paths, linked_library_paths

# Collection-only link test in a blank scene proves the library is independently importable.
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(asset_path, link=True) as (data_from, data_to):
    assert collection_name in data_from.collections
    data_to.collections = [collection_name]
linked_collection = next(col for col in data_to.collections if col and col.name == collection_name)
bpy.context.scene.collection.children.link(linked_collection)
export_object_count = len(linked_collection.objects)
assert export_object_count > 0
assert all(obj.type not in {'CAMERA', 'LIGHT'} for obj in linked_collection.objects)

payload = {
    'status': 'passed',
    'asset_path': 'modular/buildings/biochemistry_building.blend',
    'scene': 'Scene',
    'collection': collection_name,
    'reopened_object_count': reopened_object_count,
    'reopened_mesh_count': reopened_mesh_count,
    'reopened_font_count': reopened_font_count,
    'reopened_camera_or_light_count_in_asset_collection': 0,
    'collection_only_link_import_object_count': export_object_count,
    'collection_only_link_camera_or_light_count': 0,
    'gis_centroid_origin_error_m': origin_error,
    'gis_footprint_unique_vertex_count': len(gis_local),
    'shell_max_nearest_vertex_error_m': max_vertex_error,
    'evaluated_local_bounds_m': bounds,
    'vertical_extent_m': bounds[2][1] - bounds[2][0],
    'roof_equipment_centers': roof_equipment,
    'external_image_paths': external_image_paths,
    'linked_library_paths': linked_library_paths,
    'height_status': 'estimated; GIS field units are undocumented',
    'independent_grade': None,
}
with open(result_path, 'w', encoding='utf-8') as f:
    json.dump(payload, f, indent=2)
print(json.dumps(payload, indent=2))
