import bpy, bmesh, json, hashlib, math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / 'modular/buildings/massing_west_lafayette_intermediate_school_d72f0fa.blend'
AUDIT = ROOT / 'audit/west_lafayette_intermediate_school'
OSM = AUDIT / 'sources/osm_way_772742586_full.json'
SCENE_NAME = 'Building_massing_west_lafayette_intermediate_school_d72f0fa'
COLLECTION_NAME = 'Asset_massing_west_lafayette_intermediate_school_d72f0fa'

scene = bpy.data.scenes.get(SCENE_NAME)
collection = bpy.data.collections.get(COLLECTION_NAME)
assert scene is not None and collection is not None
objects = list(collection.all_objects)
meshes = [o for o in objects if o.type == 'MESH']
assert len(objects) > 1000 and meshes
shell = bpy.data.objects.get('GIS 772742586 | exact connected school footprint')
assert shell is not None

data = json.loads(OSM.read_text(encoding='utf-8'))
way = next(e for e in data['elements'] if e.get('type') == 'way' and e.get('id') == 772742586)
nodes = {e['id']: (e['lon'], e['lat']) for e in data['elements'] if e.get('type') == 'node'}
source = []
for node_id in way['nodes']:
    lon, lat = nodes[node_id]
    source.append(((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
                   (lat - 40.4274) * 111040.0))
if source and source[0] == source[-1]:
    source.pop()

def point_in_ring(x, y):
    inside = False
    for (x1, y1), (x2, y2) in zip(source, source[1:] + source[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            inside = not inside
    if inside:
        return True
    # Treat exact mapped-boundary vertices as contained within numerical tolerance.
    for (x1, y1), (x2, y2) in zip(source, source[1:] + source[:1]):
        dx, dy = x2 - x1, y2 - y1
        t = max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / max(dx * dx + dy * dy, 1e-20)))
        if math.hypot(x - (x1 + t * dx), y - (y1 + t * dy)) <= 1e-4:
            return True
    return False

base = []
for vertex in shell.data.vertices:
    p = shell.matrix_world @ vertex.co
    if abs(p.z) < 1e-5:
        base.append((round(p.x, 7), round(p.y, 7)))
base = list(dict.fromkeys(base))
errors = [min(math.hypot(x - bx, y - by) for bx, by in base) for x, y in source]
bm = bmesh.new()
bm.from_mesh(shell.data)
bm.normal_update()
shell_diag = {
    'vertices': len(bm.verts), 'edges': len(bm.edges), 'faces': len(bm.faces),
    'boundary_edges': sum(e.is_boundary for e in bm.edges),
    'nonmanifold_edges': sum(not e.is_manifold for e in bm.edges),
    'zero_area_faces': sum(f.calc_area() < 1e-10 for f in bm.faces),
    'signed_volume_m3': round(bm.calc_volume(signed=True), 6) if bm.edges and all(e.is_manifold for e in bm.edges) else None,
}
bm.free()

room_markers = [o for o in objects if o.type == 'MESH' and 'classroom_center_xy' in o]
room_centers = []
for o in room_markers:
    x, y = o['classroom_center_xy']
    room_centers.append({'room': o.name.split('|')[0].strip(), 'wing': o.get('classroom_wing'),
                         'x': float(x), 'y': float(y), 'inside': point_in_ring(float(x), float(y))})
classroom_prefixes = tuple(f'Classroom {i:02d} |' for i in range(1,37))
classroom_meshes = [o for o in meshes if o.name.startswith(classroom_prefixes)]
outside_classroom_vertices = []
for o in classroom_meshes:
    for v in o.data.vertices:
        p = o.matrix_world @ v.co
        if not point_in_ring(p.x, p.y):
            outside_classroom_vertices.append({'object': o.name, 'x': p.x, 'y': p.y})

world_vertices = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
bounds = [[min(v[i] for v in world_vertices), max(v[i] for v in world_vertices)] for i in range(3)]
image_refs = []
for image in bpy.data.images:
    if image.source == 'FILE' and image.filepath:
        path = Path(bpy.path.abspath(image.filepath))
        image_refs.append({'name': image.name, 'filepath': str(path), 'exists': path.exists(), 'packed': image.packed_file is not None})
materials = sorted({slot.material.name for o in meshes for slot in o.material_slots if slot.material})
subcollections = {c.name: len(c.all_objects) for c in collection.children}
feature_counts = {
    'classroom_center_markers': len(room_markers),
    'classroom_mesh_objects': len(classroom_meshes),
    'student_tables': sum('student table' in o.name for o in objects),
    'student_chair_seats': sum('student chair seat' in o.name for o in objects),
    'teacher_desks': sum('teacher desk' in o.name for o in objects),
    'teaching_boards': sum('teaching board' in o.name for o in objects),
    'roof_plates': sum(o.name.startswith('Classroom wing roof plate') for o in objects),
    'roof_monitors': sum(o.name.startswith('Roof monitor') for o in objects),
    'roof_mechanical_screens': sum(o.name.startswith('Roof mechanical screen') for o in objects),
    'gym_bleacher_tiers': sum('folding bleacher tier' in o.name for o in objects),
    'gym_trusses': sum('gym red steel roof truss' in o.name.lower() for o in objects),
    'gym_court_markings': sum('Gym court |' in o.name for o in objects),
}
report = {
    'fresh_open': True, 'blender_version': bpy.app.version_string,
    'asset_sha256': hashlib.sha256(ASSET.read_bytes()).hexdigest(), 'asset_size_bytes': ASSET.stat().st_size,
    'scene': scene.name, 'collection': collection.name,
    'object_count': len(objects), 'mesh_object_count': len(meshes),
    'mesh_vertex_count': sum(len(o.data.vertices) for o in meshes),
    'mesh_polygon_count': sum(len(o.data.polygons) for o in meshes), 'bounds_world_m': bounds,
    'osm_way_id': way['id'], 'osm_tags': way.get('tags', {}),
    'osm_closed_node_count': len(way['nodes']), 'osm_unique_perimeter_nodes': len(source),
    'shell_base_unique_vertices': len(base),
    'footprint_max_nearest_vertex_error_m': max(errors),
    'footprint_rms_nearest_vertex_error_m': math.sqrt(sum(e * e for e in errors) / len(errors)),
    'shell_mesh_diagnostics': shell_diag, 'object_counts_by_subcollection': subcollections,
    'named_feature_counts': feature_counts,
    'classroom_placement': {
        'expected_count': 36, 'center_count': len(room_centers),
        'centers_inside_count': sum(r['inside'] for r in room_centers),
        'outside_centers': [r for r in room_centers if not r['inside']],
        'classroom_mesh_object_count': len(classroom_meshes),
        'classroom_mesh_vertex_outside_count': len(outside_classroom_vertices),
        'outside_classroom_vertices_sample': outside_classroom_vertices[:20],
        'centers': room_centers,
    },
    'material_names': materials, 'image_dependencies': image_refs,
    'unpacked_missing_images': [x for x in image_refs if not x['packed'] and not x['exists']],
}
assert report['osm_unique_perimeter_nodes'] == 45 and report['shell_base_unique_vertices'] == 45
assert report['footprint_max_nearest_vertex_error_m'] < 0.001
assert shell_diag['boundary_edges'] == 0 and shell_diag['nonmanifold_edges'] == 0
assert len(room_markers) == 36 and report['classroom_placement']['centers_inside_count'] == 36
print('WLIS_OUTSIDE_CLASSROOM_VERTICES', json.dumps(outside_classroom_vertices[:20]))
assert not outside_classroom_vertices, f"{len(outside_classroom_vertices)} classroom mesh vertices outside GIS shell"
assert not report['unpacked_missing_images']
(AUDIT / 'fresh_open_validation_r3.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

evidence_path = AUDIT / 'evidence.json'
evidence = json.loads(evidence_path.read_text(encoding='utf-8'))
evidence['asset_sha256'] = report['asset_sha256']
evidence['asset_size_bytes'] = report['asset_size_bytes']
evidence['geometry_review'] = {
    'status': 'R3 standalone fresh-open validation passed in Blender 5.2.3; see fresh_open_validation_r3.json',
    'validation_file': 'audit/west_lafayette_intermediate_school/fresh_open_validation_r3.json',
    'fresh_open': True, 'scene': report['scene'], 'collection': report['collection'],
    'object_count': report['object_count'], 'mesh_object_count': report['mesh_object_count'],
    'mesh_vertices': report['mesh_vertex_count'], 'mesh_polygons': report['mesh_polygon_count'],
    'bounds_world_m': bounds,
    'footprint_comparison': {
        'source': 'OSM way 772742586, 45 unique perimeter nodes',
        'shell_base_unique_vertices': len(base),
        'max_nearest_vertex_error_m': report['footprint_max_nearest_vertex_error_m'],
        'rms_nearest_vertex_error_m': report['footprint_rms_nearest_vertex_error_m'],
        'shell_mesh_diagnostics': shell_diag,
    },
    'classroom_placement': report['classroom_placement'],
    'roof_and_facade': 'Plan-view roof bars are aligned diagonally to show crossing classroom wings, with a lower southeast gym/multipurpose roof cluster. The raised central node has four glazed clerestory ribbons and red mullions. The entry portal has paired brick piers, red steel columns and open-web truss detail, a sloped glazed canopy, and a broad glazed vestibule. Exact elevations and facade stationing are estimates.',
    'interior': '36 compact schematic classroom rooms are packed in NW, SW, and NE wing zones, 12 per zone. Each room center and complete 4.24 m square boundary is checked against the GIS polygon before modeling; the fresh-open validation also checks every classroom mesh vertex. Each room has partitions, a corridor door, clerestory, three student tables/chairs, teacher desk, and teaching board. Room positions and dimensions remain unverified by an authoritative floor plan.',
    'material_names': materials, 'external_image_dependencies': image_refs,
    'limitations': 'OSM is community mapping, Esri imagery has no capture date or explicit pixel georeferencing, and no measured elevation, dimensioned floor plan, or roof schedule was found. Vertical dimensions, exact interior arrangement, and facade stations are estimates.',
    'previews_reviewed': [
        'preview_r3_aerial.png', 'preview_r3_main_entry.png', 'preview_r3_northwest.png',
        'preview_r3_gym.png', 'preview_r3_interior_cutaway.png',
        'preview_r3_classroom_interior.png', 'preview_r3_gym_interior.png'],
}
evidence_path.write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
print('WLIS_FRESH_OPEN_R3 ' + json.dumps(report))
