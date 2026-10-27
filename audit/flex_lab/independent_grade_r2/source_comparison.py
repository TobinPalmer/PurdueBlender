import json
from pathlib import Path
from shapely.geometry import LineString

here = Path(__file__).resolve().parent
root = here.parents[2]
probe = json.loads((here / 'probe.json').read_text())
refs = json.loads((root / 'audit/official_building_references.json').read_text())
manifest = json.loads((root / 'modular/manifest.json').read_text())
feature = next(x for x in refs['buildings'] if x['fid'] == 909)
asset = next(x for x in manifest['assets'] if x['id'] == 'flex_lab')
ring = feature['rings_xy_m'][0]
origin = asset['placement_origin_xy_m']
model_xy = probe['shell_unique_local_xy_vertices']
model_campus = [(x + origin[0], y + origin[1]) for x, y in model_xy]
source_line = LineString(ring)
model_line = LineString(model_campus)
source_bbox_center = [
    (min(p[0] for p in ring) + max(p[0] for p in ring)) / 2,
    (min(p[1] for p in ring) + max(p[1] for p in ring)) / 2,
]
comparison = {
    'official_feature': {'provider': refs['source'], 'feature_id': feature['fid'], 'name': feature['name'], 'snapshot_retrieved': refs['snapshot_date'], 'coordinate_frame': refs['coordinates']},
    'model_origin_xy_m': origin,
    'source_bbox_center_xy_m': source_bbox_center,
    'origin_delta_from_bbox_center_m': [origin[i] - source_bbox_center[i] for i in range(2)],
    'source_ring_vertex_count_closed': len(ring),
    'model_shell_unique_xy_vertex_count': len(model_xy),
    'symmetric_boundary_hausdorff_m': source_line.hausdorff_distance(model_line),
    'source_service_edit_date': 'not supplied by source metadata',
    'caveat': 'GIS is an official campus-map polygon in an approximate project-local geographic frame, not a certified survey. Hausdorff comparison is against the retrieved 2026-10-22 snapshot; it does not establish wall-to-outline offset, overhangs, or subsequent source updates.'
}
(here / 'gis_comparison.json').write_text(json.dumps(comparison, indent=2) + '\n', encoding='utf-8')
result = {
  'building': 'Flex Lab',
  'asset': 'modular/buildings/flex_lab.blend',
  'sha256': probe['sha256'],
  'expected_sha256': probe['expected_sha256'],
  'fresh_open': probe['fresh_open'],
  'blender_version': probe['blender_version'],
  'pass_threshold': 8.0,
  'score': 8.4,
  'pass': True,
  'criteria': [
    {'criterion':'Identity / footprint','score':2.0,'max':2.0,'findings':'Official Purdue GIS FID 909 identifies Flex Laboratories. The model contains the 170-vertex shell preserved exactly from its baseline; after applying the manifest placement origin, the 85-point modeled boundary is within 0.098 m symmetric Hausdorff distance of the 91-point ring in the retrieved official GIS snapshot. This supports the identity and plan outline; GIS is not a certified survey.'},
    {'criterion':'Position / orientation / scale','score':1.8,'max':2.0,'findings':'The local model is consistently expressed in meters, with no transform change to the preserved shell. Manifest XY origin differs from official polygon AABB center by under 0.001 m, and its minimum-rotated rectangle is approximately 98.45 by 32.51 m at 90.06 degrees east-CCW. Asset is intentionally local-coordinate and master marker supplies placement; this independent grade did not complete a separate read of the full master file, so final in-master marker linkage is not independently scored at full credit.'},
    {'criterion':'Floors / roof','score':1.5,'max':2.0,'findings':'Three above-grade stories and a basement are supported by CE Solutions / Purdue project references. The shell reaches 14.8 m, but precise floor-to-floor heights and total height are estimates. High-bay roof monitor and roof form are interpretive rather than dimensioned/as-built.'},
    {'criterion':'Facade / entrances / architecture','score':1.5,'max':2.0,'findings':'The R2 shell openings reveal three-story curtainwall across the south entry and 11 long-façade bays; brick planes, changing glass/aluminum rhythm, mullions, spandrels, vestibule, two supports, and one canopy are modeled. Canopy projection is 6.10 m, matching the published 20 ft dimension. The photos support the composition but not bay widths/heights; canopy framing and facade rhythms remain simplified and the review render reads dark/diagrammatic. Interior layout and furnishings are schematic, not plan-verified.'},
    {'criterion':'Modular export / portability / evidence','score':1.6,'max':2.0,'findings':'Fresh-opened in Blender 5.2.3 with exact SHA match, expected Scene and linked Asset_flex_lab collection, 407 objects, no missing external images, and no libraries linked at initial open. Evidence covers Ennead, CE Solutions, Purdue identity/use, and GIS. Evidence quality loses credit because the R2 source register says GIS vintage/CRS was not retained, while official_building_references.json and manifest metadata record a 2026-10-22 retrieval snapshot, approximate coordinate transform, and source CRS caveat. The source register also labels AW07 as façade although the local AW07 reference is an interior image.'}
  ],
  'limitations': [
    'Published photos are not dimensioned elevations; exact facade bay widths, opening heights and floor elevations remain estimates.',
    'Interior organization is schematic and not verified against construction or current plans.',
    'Official source snapshot retrieval date is recorded as 2026-10-22, but the GIS feature edit/vintage date is not supplied; coordinate transform is an approximate local frame, not a certified survey.',
    'The assessment used the separately fresh-opened standalone asset; full master marker-link verification was not completed by this grader.'
  ],
  'evidence_files': [
    'probe.json', 'gis_comparison.json', 'source_comparison.py',
    'audit/flex_lab/fresh_open_validation_r2.json',
    'audit/flex_lab/evidence_r2.json',
    'audit/official_building_references.json',
    'modular/manifest.json',
    'audit/flex_lab/flex_r2_front.png',
    'audit/flex_lab/flex_r2_oblique.png',
    'audit/flex_lab/flex_r2_interior.png',
    'audit/flex_lab/sources/ennead_AW19_entry.jpg',
    'audit/flex_lab/sources/ennead_AW06_curtainwall.jpg',
    'audit/flex_lab/sources/ce_solutions_entry.jpg'
  ]
}
(here / 'result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'score':result['score'],'pass':result['pass'],'gis':comparison},indent=2))
