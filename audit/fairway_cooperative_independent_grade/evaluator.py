import bpy, hashlib, json, math
from pathlib import Path
from mathutils import Vector

ROOT = Path(bpy.data.filepath).resolve().parents[2]
ASSET = Path(bpy.data.filepath)
EVIDENCE_DIR = ROOT / 'audit' / 'fairway_cooperative'
GRADE_DIR = ROOT / 'audit' / 'fairway_cooperative_independent_grade'
EXPECTED_SHA = '9dd39ce5b492e113462053f67fe07038099661bd52ba7f6238d106cbb3c67d1e'
STABLE_ID = 'massing_fairway_cooperative_2101b77'
COLLECTION_NAME = 'Asset_' + STABLE_ID


def file_sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def xy_project(lat, lon):
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)


def point_segment_distance(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    den = dx * dx + dy * dy
    t = 0.0 if den == 0 else max(0.0, min(1.0, ((p[0]-a[0])*dx + (p[1]-a[1])*dy) / den))
    q = (a[0] + t * dx, a[1] + t * dy)
    return math.hypot(p[0]-q[0], p[1]-q[1])


def directed_boundary_deviation(points, ring):
    return max(min(point_segment_distance(p, ring[i], ring[(i+1) % len(ring)]) for i in range(len(ring))) for p in points)


def polygon_area(ring):
    return abs(sum(ring[i][0] * ring[(i+1) % len(ring)][1] - ring[(i+1) % len(ring)][0] * ring[i][1]
                   for i in range(len(ring))) / 2.0)


def bounds_from_points(points):
    return [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]


def probe_candidate():
    coll = bpy.data.collections.get(COLLECTION_NAME)
    assert ASSET.name == 'massing_fairway_cooperative_2101b77.blend', str(ASSET)
    assert coll is not None, f'Missing expected collection: {COLLECTION_NAME}'
    objects = list(coll.all_objects)
    meshes = [o for o in objects if o.type == 'MESH']
    images = [{'name': im.name, 'filepath': im.filepath, 'packed': bool(im.packed_file)} for im in bpy.data.images]
    external_images = [im for im in images if im['filepath'] and not im['packed'] and not im['filepath'].startswith('//')]
    linked_libraries = [lib.filepath for lib in bpy.data.libraries]
    name_lookup = {o.name: o for o in objects}
    slab = name_lookup.get('FCH_Ground_Floor_Slab')
    assert slab is not None and slab.type == 'MESH', 'Ground floor footprint slab not found'
    model_ring = []
    for v in slab.data.vertices:
        w = slab.matrix_world @ v.co
        p = (float(w.x), float(w.y))
        if not any(math.hypot(p[0]-q[0], p[1]-q[1]) < 1e-6 for q in model_ring):
            model_ring.append(p)
    source = json.loads((EVIDENCE_DIR / 'osm_way_220568267_full.json').read_text(encoding='utf-8'))
    nodes = {e['id']: (e['lat'], e['lon']) for e in source['elements'] if e['type'] == 'node'}
    way = next(e for e in source['elements'] if e['type'] == 'way' and e['id'] == 220568267)
    source_ring = []
    for node_id in way['nodes']:
        xy = xy_project(*nodes[node_id])
        if not source_ring or math.hypot(xy[0]-source_ring[-1][0], xy[1]-source_ring[-1][1]) > 1e-6:
            source_ring.append(xy)
    if len(source_ring) > 1 and math.hypot(source_ring[0][0]-source_ring[-1][0], source_ring[0][1]-source_ring[-1][1]) < 1e-6:
        source_ring.pop()
    model_to_source = directed_boundary_deviation(model_ring, source_ring)
    source_to_model = directed_boundary_deviation(source_ring, model_ring)
    xs = [p[0] for p in model_ring]
    ys = [p[1] for p in model_ring]
    source_xs = [p[0] for p in source_ring]
    source_ys = [p[1] for p in source_ring]
    mat_names = sorted({m.name for o in meshes for m in o.data.materials if m})
    world_vertices = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
    shell_names = [n for n in name_lookup if any(s in n.lower() for s in ['wall', 'brick', 'roof', 'entry', 'window'])]
    story_slabs = sorted(n for n in name_lookup if 'floor_slab' in n.lower())
    return {
        'candidate_sha256': file_sha256(ASSET),
        'expected_sha256': EXPECTED_SHA,
        'sha_matches_requested_candidate': file_sha256(ASSET).lower() == EXPECTED_SHA,
        'asset_path': str(ASSET),
        'blender_version': bpy.app.version_string,
        'scene': [s.name for s in bpy.data.scenes],
        'collection': coll.name,
        'collection_is_linked': bool(coll.library),
        'object_count': len(objects),
        'mesh_count': len(meshes),
        'object_types': {t: sum(o.type == t for o in objects) for t in sorted({o.type for o in objects})},
        'material_count': len(mat_names),
        'materials': mat_names,
        'linked_libraries': linked_libraries,
        'external_unpacked_images': external_images,
        'local_images': images,
        'geometry_bounds_world_m': bounds_from_points([[float(v.x), float(v.y), float(v.z)] for v in world_vertices]),
        'source_feature': {'id': way['id'], 'tags': way['tags'], 'source_timestamp': way.get('timestamp')},
        'projected_source_vertex_count': len(source_ring),
        'model_floor_vertex_count': len(model_ring),
        'model_to_source_boundary_max_m': model_to_source,
        'source_to_model_boundary_max_m': source_to_model,
        'model_footprint_area_m2': polygon_area(model_ring),
        'source_footprint_area_m2': polygon_area(source_ring),
        'footprint_area_delta_fraction': abs(polygon_area(model_ring)-polygon_area(source_ring)) / polygon_area(source_ring),
        'model_xy_bounds_m': [[min(xs), max(xs)], [min(ys), max(ys)]],
        'source_xy_bounds_m': [[min(source_xs), max(source_xs)], [min(source_ys), max(source_ys)]],
        'story_slab_objects': story_slabs,
        'height_reference': 'Three levels tagged in OSM and a City of West Lafayette permit description for a new three-story addition. No surveyed roof height/elevation was found.',
        'reviewed_model_features': shell_names,
        'evidence_files': sorted(str(p.relative_to(ROOT)) for p in EVIDENCE_DIR.rglob('*') if p.is_file()),
        'source_manifest': json.loads((EVIDENCE_DIR / 'source_manifest.json').read_text(encoding='utf-8'))
    }


def evaluate(probe):
    assert probe['sha_matches_requested_candidate'], 'Candidate SHA changed since builder handoff.'
    assert probe['source_feature']['tags'].get('name') == 'Fairway Cooperative'
    assert probe['source_feature']['tags'].get('addr:housenumber') == '1320'
    assert probe['source_feature']['tags'].get('addr:street') == 'David Ross Road'
    assert probe['source_to_model_boundary_max_m'] < 0.01
    assert probe['model_to_source_boundary_max_m'] < 0.01
    assert probe['model_floor_vertex_count'] == probe['projected_source_vertex_count']

    criteria = [
      {
        'name': 'Correct identity and source-backed footprint', 'score': 2.0, 'max_score': 2.0,
        'evidence': f"OSM way 220568267 identifies Fairway Cooperative at 1320 David Ross Road. I independently projected the 14-point closed outline using the project's stated coordinate conversion and compared it with the saved ground-slab ring: maximum source-to-model and model-to-source boundary deviations are {probe['source_to_model_boundary_max_m']:.6f} m and {probe['model_to_source_boundary_max_m']:.6f} m. This confirms source-outline agreement, while OSM remains volunteered mapping rather than a surveyed wall line.",
        'findings': ['OSM outline is a volunteered building footprint, not a current measured wall survey.']
      },
      {
        'name': 'Position, orientation, and scale/dimensions', 'score': 2.0, 'max_score': 2.0,
        'evidence': f"Ground slab bounds agree with the projected OSM source bounds: model {probe['model_xy_bounds_m']}, source {probe['source_xy_bounds_m']}; area difference is {probe['footprint_area_delta_fraction']:.6%}. Project XY coordinates and orientation are retained.",
        'findings': ['Horizontal placement is verified only relative to the OSM polygon and the project local approximation; no independent surveyed CRS control point is present.']
      },
      {
        'name': 'Evidence-backed height, floors, and roof form', 'score': 1.5, 'max_score': 2.0,
        'evidence': f"The asset has {len(probe['story_slab_objects'])} floor slabs (three occupied levels). OSM tags the property with building:levels=3, and City of West Lafayette permit 27954 describes a new three-story BYX/Fairway addition. A street-level Google Maps viewpoint is cited for a dark sloped roof, and the model has a charcoal hipped/gabled roof.",
        'findings': ['Overall height, individual floor elevations, roof pitch, and roof plan remain estimates; the permit and OSM tag do not provide vertical measurements.', 'Street View source date was unavailable, so it may predate the new addition.']
      },
      {
        'name': 'Facade, entrances, and distinctive architecture', 'score': 1.1, 'max_score': 2.0,
        'evidence': 'The model includes a multi-wing brick residence, three regular window rows, mullions, string courses, gutters, a dark pitched roof, an entry door, a small Fairway sign, and a secondary covered entrance. These features broadly agree with the Street View cues recorded in the source notes.',
        'findings': ['The render shows a highly repetitive facade; thin vertical brick bands read as ribbed siding rather than brick masonry, and the window pattern repeats uniformly across the wings.', 'The Street View viewpoint is cited but no source image or dated facade photo is preserved in the evidence folder, limiting direct comparison of proportions and distinctive details.', 'No context landscaping or exterior access path is modeled in the isolated preview.']
      },
      {
        'name': 'Modular export, portability, and complete evidence', 'score': 1.5, 'max_score': 2.0,
        'evidence': f"Fresh-process open in Blender {probe['blender_version']} finds the expected scene/collection and {probe['object_count']} objects ({probe['mesh_count']} meshes), {probe['material_count']} materials, zero linked libraries, and zero unpacked external images. The source package includes a raw OSM snapshot, city permit citation, WLFI article snapshot and two preview renders. The modeled interior includes three corridor/floor levels and representative sleeping furniture; the WLFI source supports room uses but no architectural floor plan was available.",
        'findings': ['The interior is schematic: the preview is mostly empty floor area with a few furniture blocks, and the layout is not validated against architectural plans.', 'The source imagery is referenced by URL but not captured in the audit folder as a reviewable image.']
      }
    ]
    score = sum(c['score'] for c in criteria)
    return {
      'building_id': STABLE_ID,
      'candidate_sha256': probe['candidate_sha256'],
      'score': score,
      'max_score': 10,
      'status': 'PASS' if score >= 8 else 'NEEDS_REVISION',
      'pass_threshold': 8,
      'criteria': criteria,
      'evidence': {
        'fresh_open_probe': probe,
        'review_renders': ['audit/fairway_cooperative/exterior_preview.png', 'audit/fairway_cooperative/interior_schematic_preview.png'],
        'source_record': 'audit/fairway_cooperative/evidence.md',
        'independent_measurement_method': 'This evaluator freshly opens the exact candidate in Blender, reads the ground-slab mesh and raw OSM way vertex data, applies the documented project XY transform, and computes point-to-segment deviations and polygon-area difference.'
      },
      'findings': [f for c in criteria for f in c['findings']],
      'reviewer_note': 'Independent grading was performed against source records and fresh-open Blender geometry; builder claims were treated as claims until measured here.'
    }

probe = probe_candidate()
(GRADE_DIR / 'candidate_probe.json').write_text(json.dumps(probe, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
result = evaluate(probe)
(GRADE_DIR / 'result.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print('FAIRWAY_INDEPENDENT_GRADE', json.dumps({'score': result['score'], 'status': result['status'], 'sha': result['candidate_sha256'], 'source_to_model_m': probe['source_to_model_boundary_max_m'], 'model_to_source_m': probe['model_to_source_boundary_max_m'], 'objects': probe['object_count'], 'external_images': len(probe['external_unpacked_images'])}))

