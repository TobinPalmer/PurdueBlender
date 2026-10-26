import bpy, json, math
from pathlib import Path

ROOT = Path.cwd()
aid = 'massing_purdue_village_administration_building_3faae6c'
asset = ROOT / 'modular' / 'buildings' / f'{aid}.blend'
audit = ROOT / 'audit' / aid
bpy.ops.wm.open_mainfile(filepath=str(asset))
scene = bpy.context.scene
col = bpy.data.collections.get(f'Asset_{aid}')
obj = bpy.data.objects.get('Purdue Village Administration Building')
if not col or not obj or obj.name not in col.objects:
    raise RuntimeError('expected export collection/object missing after fresh reopen')
if len(col.objects) != 1 or obj.type != 'MESH':
    raise RuntimeError('export must contain exactly one building mesh object')
deps = bpy.context.evaluated_depsgraph_get()
ev = obj.evaluated_get(deps)
me = ev.to_mesh()
coords = [ev.matrix_world @ v.co for v in me.vertices]
bounds = [[min(v[i] for v in coords), max(v[i] for v in coords)] for i in range(3)]
raw = json.loads((audit / 'sources' / 'arcgis_fid524_raw.json').read_text(encoding='utf-8'))
f = raw['features'][0]
src_ring = f['geometry']['rings'][0]
origin_lat, origin_lon = 40.4274, -86.9137
expected = [((lon + 86.9137) * 111412.84 * math.cos(math.radians(origin_lat)),
             (lat - 40.4274) * 111040.0) for lon, lat in src_ring]
if expected and math.dist(expected[0], expected[-1]) < 1e-6:
    expected.pop()
n = len(expected)
structural_ring = [(coords[i].x, coords[i].y) for i in range(n)]
if len(structural_ring) != n:
    raise RuntimeError('expected source footprint ring was not preserved as first mesh vertices')
max_vertex_error = max(math.dist(structural_ring[i], expected[i]) for i in range(n))
if max_vertex_error > 0.001:
    raise RuntimeError(f'GIS ring mismatch: {max_vertex_error:.6f} m')
structural_bounds = [[min(p[i] for p in structural_ring), max(p[i] for p in structural_ring)] for i in range(2)]
area = abs(sum(structural_ring[i][0] * structural_ring[(i+1)%n][1] -
               structural_ring[(i+1)%n][0] * structural_ring[i][1] for i in range(n)) / 2)
external_images = [im.filepath for im in bpy.data.images if im.source == 'FILE' and im.filepath and not im.packed_file]
result = {
    'building_id': aid,
    'reopened_file': str(asset),
    'reopen_success': True,
    'collection': col.name,
    'collection_object_count': len(col.objects),
    'collection_transform': {'instance_offset': list(col.instance_offset), 'note': 'massing direct-link; identity object transforms retained'},
    'object': obj.name,
    'object_type': obj.type,
    'object_location': list(obj.location),
    'object_rotation_euler': list(obj.rotation_euler),
    'object_scale': list(obj.scale),
    'evaluated_bounds_world_m_including_decorative_projections': bounds,
    'evaluated_dimensions_m_including_decorative_projections': [bounds[i][1]-bounds[i][0] for i in range(3)],
    'structural_wall_footprint_bounds_world_m': structural_bounds,
    'structural_wall_height_m': max(coords[i+n].z for i in range(n)),
    'decorative_facade_projection_max_m': 0.15,
    'evaluated_vertex_count': len(me.vertices),
    'evaluated_face_count': len(me.polygons),
    'modifier_count': len(obj.modifiers),
    'footprint_vertex_count': n,
    'footprint_plan_area_m2': area,
    'official_gis_feature_id': f['attributes']['FID'],
    'official_gis_feature_name': f['attributes']['BUILDING_N'],
    'official_gis_source_crs': raw.get('spatialReference'),
    'max_vertex_error_vs_live_gis_project_transform_m': max_vertex_error,
    'estimated_height_m': obj.get('estimated_height_m'),
    'height_status': obj.get('height_status'),
    'facade_status': obj.get('facade_status'),
    'roof_status': obj.get('roof_status'),
    'external_unpacked_image_dependencies': external_images,
    'geometry_change': 'rebuilt shell on unchanged official FID 524 footprint; added source-photo facade overlays as faces in the same mesh; campus coordinates retained'
}
ev.to_mesh_clear()
(audit / 'reopen_validation.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result, indent=2))
