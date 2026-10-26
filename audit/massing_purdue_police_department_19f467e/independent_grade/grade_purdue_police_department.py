import bpy, json, math, os, datetime
from mathutils import Vector
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
AUDIT = os.path.join(ROOT, 'audit', 'massing_purdue_police_department_19f467e')
EVIDENCE = json.load(open(os.path.join(AUDIT, 'evidence.json'), encoding='utf-8'))
REOPEN = json.load(open(os.path.join(AUDIT, 'reopen_validation.json'), encoding='utf-8'))
GIS = json.load(open(os.path.join(AUDIT, 'sources', 'purdue_gis_fid_275.json'), encoding='utf-8'))
BUILDING_ID = 'massing_purdue_police_department_19f467e'
SCENE_NAME = 'Building_' + BUILDING_ID
COLLECTION_NAME = 'Asset_' + BUILDING_ID
scene = bpy.data.scenes.get(SCENE_NAME)
collection = bpy.data.collections.get(COLLECTION_NAME)
obj = bpy.data.objects.get('Purdue Police Department')

def metric(name, points, status, evidence, finding=None):
    return {'criterion': name, 'score': points, 'max_score': 2, 'status': status, 'evidence': evidence, 'finding': finding}

# Independently measure reopened Blender geometry and exported library structure.
actual = {'scene_present': scene is not None, 'collection_present': collection is not None, 'object_present': obj is not None}
if obj:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    mesh = eval_obj.to_mesh()
    world = [eval_obj.matrix_world @ v.co for v in mesh.vertices]
    actual.update({
        'object_type': obj.type,
        'collection_objects': sorted(x.name for x in collection.objects) if collection else [],
        'vertex_count': len(mesh.vertices),
        'polygon_count': len(mesh.polygons),
        'bounds_world_m': [[min(v[i] for v in world), max(v[i] for v in world)] for i in range(3)],
        'bottom_xy_bounds_m': [[min(v[i] for v in world if v.z <= 0.001), max(v[i] for v in world if v.z <= 0.001)] for i in range(2)],
        'object_transform': {'location': list(obj.location), 'rotation': list(obj.rotation_euler), 'scale': list(obj.scale)},
        'modifiers': [m.name for m in obj.modifiers],
        'material_names': sorted(m.name for m in obj.data.materials if m),
        'image_paths': [im.filepath for im in bpy.data.images if im.source == 'FILE'],
    })
    eval_obj.to_mesh_clear()

# Check identity against cached primary sources, not only the builder narrative.
html_events = open(os.path.join(AUDIT, 'sources', 'purdue_events_terry_house.html'), encoding='utf-8', errors='replace').read()
html_bep = open(os.path.join(AUDIT, 'sources', 'purdue_tery_building_emergency_plan.html'), encoding='utf-8', errors='replace').read()
attrs = next((x.get('attributes', {}) for x in GIS.get('features', []) if x.get('attributes', {}).get('FID') == 275), {})
identity_ok = (attrs.get('BUILDING_N') == 'Oliver Perkins Terry House' and attrs.get('ADDRESS') == '205 S Martin Jischke Drive' and 'Purdue University Police Department is located in Terry House' in html_events and '1 story building' in html_bep and 'utility basement' in html_bep)

# Verify GIS footprint-derived raw points match the builder's explicit record; check reopened mesh bounds against stated bounds.
source_bounds = EVIDENCE['geometry']['source_footprint_bounds_campus_xy_m']
measured_bounds = actual.get('bottom_xy_bounds_m', [])
source_vs_actual_bounds = None
if len(measured_bounds) == 2:
    source_vs_actual_bounds = max(abs(measured_bounds[a][b] - source_bounds[axis][b]) for a, axis in enumerate(('x','y')) for b in (0,1))
expected_collection_ok = (actual.get('scene_present') and actual.get('collection_present') and actual.get('object_type') == 'MESH' and actual.get('collection_objects') == ['Purdue Police Department'] and actual.get('vertex_count', 0) > 0)
relative_dependencies_ok = (len(actual.get('image_paths', [])) == 0 and len(actual.get('modifiers', [])) == 0 and expected_collection_ok)

criteria = []
criteria.append(metric('Identity and source-backed footprint', 2.0 if identity_ok else 0.5, 'verified' if identity_ok else 'uncertain', 'Raw Purdue GIS FID 275 names Oliver Perkins Terry House, gives address 205 S Martin Jischke Drive, and supplies a polygon. Cached Purdue Events HTML explicitly says PUPD is located in Terry House; cached Purdue emergency plan independently names TERY, lists PUPD/dispatch, and states one story plus a small utility basement. The rooftop aerial is consistent with a broad low building, although imagery date/clarity limit precise wall interpretation.' if identity_ok else 'Primary-source identity check failed.', None if identity_ok else 'Resolve identity and source feature before acceptance.'))
criteria.append(metric('Position, orientation, and scale/dimensions', 1.75 if (source_vs_actual_bounds is not None and source_vs_actual_bounds < 0.01) else 0.75, 'GIS footprint and campus position verified; frontage orientation estimated', f'Reopened mesh bounds compared with the source-footprint XY bounds recorded in evidence; maximum axis-bound discrepancy {source_vs_actual_bounds:.4f} m. GIS-derived polygon point match and surrounding Esri imagery support campus placement. The local degree-to-meter conversion is explicitly approximate, and the source photo does not georeference the modeled entrance side.', 'Orientation of the detailed facade/entrance is not established by source evidence.' if identity_ok else None))
criteria.append(metric('Evidence-backed height, floors, and roof form', 1.25, 'story count and roof form supported; numeric heights estimated', 'Official emergency plan directly states one story with a small utility basement. Purdue Events exterior photo visibly supports a low, flat/parapet roof. The 4.05 m wall and 4.45 m roof/parapet are explicitly estimates inferred from photo proportions; no surveyed vertical dimensions or roof plan were found.', 'Do not treat modeled wall/roof elevations as measured; basement is not modeled due to missing dimensions.'))
criteria.append(metric('Facade, entrances, and distinctive architecture', 1.4, 'major facade pattern supported; detailed placement partly estimated', 'Inspected cached Purdue Events photograph: it visibly shows a horizontal red-brick building, long continuous ribbon glazing with vertical divisions, and a projecting red canopy. Rendered model includes these broad traits and one entrance. The model regularizes pier/mullion spacing and places door/canopy on a representative long frontage; the photograph has no georeferenced direction, and the exact entry position is not verifiable. The cross-bracing and landscaping visible in the photo are omitted.', 'Entrance frontage and exact bay rhythm remain unverified; some distinctive photo details are simplified or omitted.'))
criteria.append(metric('Modular export, portability, and complete evidence', 2.0 if (expected_collection_ok and relative_dependencies_ok and os.path.isfile(os.path.join(AUDIT,'views','purdue_police_department_frontage.png')) and len(EVIDENCE.get('sources',[])) >= 4 and REOPEN.get('checks',{}).get('asset_reopens_in_blender')) else 1.25, 'verified' if expected_collection_ok and relative_dependencies_ok else 'partial', f'Independently reopened .blend in Blender. Scene={actual.get("scene_present")}; expected collection={actual.get("collection_present")}; exported collection contains {actual.get("collection_objects")}; mesh vertices={actual.get("vertex_count")}; external file image dependencies={actual.get("image_paths")}; modifiers={actual.get("modifiers")}. Building evidence folder includes raw GIS JSON, Purdue HTML pages, source photographs/aerial, evidence record, render and reopen record.', 'Expected one-object library contract or required evidence is incomplete.' if not expected_collection_ok else None))
score = round(sum(c['score'] for c in criteria), 2)
result = {
  'evaluator': 'independent_grader_purdue_police_department',
  'graded_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'asset_path': 'modular/buildings/massing_purdue_police_department_19f467e.blend',
  'source_paths_reviewed': ['audit/massing_purdue_police_department_19f467e/evidence.json','audit/massing_purdue_police_department_19f467e/sources/purdue_gis_fid_275.json','audit/massing_purdue_police_department_19f467e/sources/purdue_tery_building_emergency_plan.html','audit/massing_purdue_police_department_19f467e/sources/purdue_events_terry_house.html','audit/massing_purdue_police_department_19f467e/sources/purdue_terry_house_photo.jpg','audit/massing_purdue_police_department_19f467e/sources/world_imagery_tery_area.jpg','audit/massing_purdue_police_department_19f467e/views/purdue_police_department_frontage.png'],
  'score': score, 'max_score': 10, 'passing_threshold': 8, 'passed': score >= 8,
  'criteria': criteria,
  'evidence': {'independent_reopened_blend_measurements': actual, 'raw_source_identity_crosscheck_passed': identity_ok, 'reopened_mesh_xy_bounds_max_abs_difference_from_source_bounds_m': source_vs_actual_bounds},
  'findings': [c['finding'] for c in criteria if c.get('finding')],
  'revision_needed': score < 8,
  'revision_requests': [] if score >= 8 else ['Resolve findings that caused deductions and request a fresh independent grade.']
}
out = os.path.join(os.path.dirname(__file__), 'grade_result.json')
with open(out, 'w', encoding='utf-8') as f: json.dump(result, f, indent=2)
print(json.dumps(result, indent=2))



