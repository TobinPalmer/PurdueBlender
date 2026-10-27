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
    'classroom_partitions': sum(o.name.startswith('Classroom ') and 'corridor partition' in o.name for o in objects),
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
    'fresh_open': True,
    'blender_version': bpy.app.version_string,
    'asset_sha256': hashlib.sha256(ASSET.read_bytes()).hexdigest(),
    'asset_size_bytes': ASSET.stat().st_size,
    'scene': scene.name, 'collection': collection.name,
    'object_count': len(objects), 'mesh_object_count': len(meshes),
    'mesh_vertex_count': sum(len(o.data.vertices) for o in meshes),
    'mesh_polygon_count': sum(len(o.data.polygons) for o in meshes),
    'bounds_world_m': bounds,
    'osm_way_id': way['id'], 'osm_tags': way.get('tags', {}),
    'osm_closed_node_count': len(way['nodes']), 'osm_unique_perimeter_nodes': len(source),
    'shell_base_unique_vertices': len(base),
    'footprint_max_nearest_vertex_error_m': max(errors),
    'footprint_rms_nearest_vertex_error_m': math.sqrt(sum(e * e for e in errors) / len(errors)),
    'shell_mesh_diagnostics': shell_diag,
    'object_counts_by_subcollection': subcollections,
    'named_feature_counts': feature_counts,
    'material_names': materials,
    'image_dependencies': image_refs,
    'unpacked_missing_images': [x for x in image_refs if not x['packed'] and not x['exists']],
}
assert report['osm_unique_perimeter_nodes'] == 45
assert report['shell_base_unique_vertices'] == 45
assert report['footprint_max_nearest_vertex_error_m'] < 0.001
assert shell_diag['boundary_edges'] == 0 and shell_diag['nonmanifold_edges'] == 0
assert not report['unpacked_missing_images']
(AUDIT / 'fresh_open_validation_r2.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

evidence_path = AUDIT / 'evidence.json'
evidence = json.loads(evidence_path.read_text(encoding='utf-8'))
evidence['asset_sha256'] = report['asset_sha256']
evidence['asset_size_bytes'] = report['asset_size_bytes']
evidence['geometry_review'] = {
    'status': 'fresh-open validation passed in Blender 5.2.3; see fresh_open_validation_r2.json',
    'validation_file': 'audit/west_lafayette_intermediate_school/fresh_open_validation_r2.json',
    'fresh_open': True,
    'scene': report['scene'], 'collection': report['collection'],
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
    'roof_and_facade': 'Stepped low-slope wing plates and coping follow the broad intersecting roof plan visible in the Esri aerial. White/light roof material reflects the aerial; roof monitors and mechanical screens are schematic and dimensions are estimated. Repeated brick, metal panel, and glazing modules remain interpretive where elevations are unavailable.',
    'interior': 'Thirty-six schematic classroom bays have corridor partitions, doors, glazing, three student tables and chairs, a teacher desk, and a teaching board each; the close top-down render makes one representative bay legible. Gym preview shows sport floor, bleacher tiers, center circle, and court lines. Room positions/dimensions are not survey verified.',
    'material_names': materials, 'external_image_dependencies': image_refs,
    'limitations': 'No measured elevations, dimensioned plan, roof schedule, or surveyed wall line found. Interior layout and all height/roof dimensions remain approximate.',
    'previews_reviewed': [
        'preview_aerial.png', 'preview_main_entry.png', 'preview_northwest.png',
        'preview_gym.png', 'preview_interior_cutaway.png', 'preview_classroom_interior.png', 'preview_gym_interior.png'],
}
evidence_path.write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
print('WLIS_FRESH_OPEN_R2 ' + json.dumps(report))
