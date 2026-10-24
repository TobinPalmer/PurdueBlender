import bpy, json, hashlib
from pathlib import Path

ROOT = Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
ASSET = ROOT / 'modular/buildings/knoy_hall.blend'
OUT = ROOT / 'audit/complete_knoy/validation_round18.json'
EVIDENCE = ROOT / 'audit/complete_knoy/evidence_round18.json'

def mesh_fingerprint(obj):
    payload = {
        'verts': [tuple(round(v, 7) for v in p.co) for p in obj.data.vertices],
        'faces': [tuple(p.vertices) for p in obj.data.polygons],
        'world': [tuple(round(v, 7) for v in row) for row in obj.matrix_world],
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene = bpy.context.scene
expected = ['KNOY_Fenestration_Ribbon_Glass', 'KNOY_Fenestration_Bronze_Mullions',
            'KNOY_Facade_Brick_Spandrels_R17', 'KNOY_Exterior_Masonry_Walls']
missing = [name for name in expected if bpy.data.objects.get(name) is None]
assert not missing, missing
assert 'ROUND 18' in bpy.data.texts['EVIDENCE_AND_INTERIOR_NOTES.txt'].as_string()
assert 'not a measured dimension' in bpy.data.objects['KNOY_Fenestration_Ribbon_Glass']['r18_facade_status']
assert scene.get('knoy_r18_review_status') == 'Evidence and uncertainty pass; no geometric changes.'
assert all(o.active_material or len(o.data.materials) for o in [bpy.data.objects[n] for n in expected])
unpacked = [img.filepath for img in bpy.data.images if img.source == 'FILE' and img.filepath and not img.packed_file]
assert not unpacked, unpacked

result = {
    'revision': 18, 'passed': True, 'reopened_saved_asset': True,
    'blender_version': bpy.app.version_string,
    'scope': 'Evidence/uncertainty metadata and embedded audit note only; no geometry, transforms, materials, or placement changed in R18.',
    'scene_object_count': len(bpy.data.objects),
    'mesh_object_count': sum(o.type == 'MESH' for o in bpy.data.objects),
    'required_knoy_objects_present': expected,
    'fingerprints': {n: mesh_fingerprint(bpy.data.objects[n]) for n in expected},
    'r18_fenestration_status': bpy.data.objects['KNOY_Fenestration_Ribbon_Glass']['r18_facade_status'],
    'r18_scene_status': scene['knoy_r18_review_status'],
    'unpacked_external_images': unpacked,
}
OUT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')

evidence = {
    'revision': 18,
    'asset': 'modular/buildings/knoy_hall.blend',
    'scope': 'Knoy-only evidence and uncertainty revision; source model geometry, placement, transforms, and materials unchanged.',
    'independent_review_disagreement': {
        'round': 17,
        'scores_out_of_10': [7.8, 7.9],
        'agreement': 'Both reviews found the modeled continuous repeated facade ribbons differ from narrow interrupted slit-like windows visible in the archival photograph.',
        'facade_measurement': 'The R17 1.40 m glass height is qualitative and unmeasured; image perspective and absent face registration prevent assigning it as-built or to all elevations.',
        'response': 'No selected-elevation interruptions were added because assigning the visible photo pattern to GIS segments is not supportable from the uncalibrated source.'
    },
    'sources': [
        {
            'title': 'Purdue Archives, Historic Facilities and Buildings Database: Maurice G. Knoy Hall of Technology',
            'url': 'https://collections.lib.purdue.edu/campus/buildings/75',
            'local_image': 'audit/complete_knoy/purdue_archives_knoy_historic_database_photo_r17.jpeg',
            'supports': 'Visible brick-heavy massing and narrow, interrupted horizontal glazing ribbons on photographed faces.',
            'does_not_support': 'Measured window dimensions, story-to-window registration, all-sided cadence, facade-face identity, or current date condition.'
        },
        {
            'title': 'Indiana 3DEP 2018 DSM tile',
            'local_source': 'audit/complete_knoy/indiana_3dep_2018_dsm_in2018_30001885_12.tif',
            'derived_analysis': 'audit/complete_knoy/roof_spatial_check_r18.json',
            'summary_ft_agl': {'p50': 59.88, 'p75': 60.12, 'p90': 63.9, 'p95': 71.81, 'p99': 75.36, 'max': 88.9},
            'valid_cells': 1126,
            'approx_bare_earth_reference_ft': 621.06,
            'supports': 'A broad roof-like surface envelope in 2018 DSM cells.',
            'does_not_support': 'Exact roof slab/parapet height, an occupied L5, penthouse geometry, or equipment location. Highest sampled cells are outside current candidate penthouse bbox.'
        },
        {
            'title': 'Purdue Polytechnic 2017 rooftop solar installation article',
            'url': 'https://old.polytechnic.purdue.edu/newsroom/new-knoy-rooftop-solar-array-generates-more-power-learning-opportunities-and-research',
            'supports': 'Historical existence of a 28-panel solar installation in 2017.',
            'does_not_support': 'Exact current layout, persistence in 2026, penthouse dimensions, or measured roof height.'
        },
        {
            'title': 'Purdue Archives, University Archives finding aid UA 141',
            'url': 'https://archives.lib.purdue.edu/repositories/2/resources/1490',
            'supports': 'Potential archival construction/floor-plan records exist for research.',
            'limitation': 'The cited finding aid is not a digitized as-built elevation or stair drawing; no new registration geometry was extracted in this revision.'
        }
    ],
    'roof_l5_status': 'Unresolved. DSM distribution is broad and includes elevated edge returns; GIS 48 ft attribute conflict remains. No roof/L5/penthouse geometry changed.',
    'circulation_status': 'No new verified dimensioned as-built circulation source found in this pass. Existing stairs and room traces remain illustrative; continuity is unverified.',
    'geometry_change': False,
    'limitations': [
        'Photo capture date and camera calibration are not established.',
        'DSM comparison uses approximate prior 21-point bare-earth median rather than surveyed datum.',
        'DSM includes trees/equipment/roof structures and cannot separate floors from roof surfaces.',
        'A digital as-built elevation or verified stair plan was not available in the reviewed sources.'
    ]
}
EVIDENCE.write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, indent=2))
print('EVIDENCE', EVIDENCE)
