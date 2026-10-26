"""Independent evaluator for Cary Quadrangle Northeast (CQNE) R2.

Run with: python evaluator.py [repo_root]
Returns the AGENT.md contract: score, max_score, criteria, evidence, findings.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE.parents[1]
ID = 'massing_cary_quadrangle_northeast_cqne_0a76fca'
ASSET = ROOT / 'modular' / 'buildings' / f'{ID}.blend'
AUDIT = ROOT / 'audit' / ID
PROBE = HERE / 'blender_probe.json'

def evaluate():
    probe = json.loads(PROBE.read_text(encoding='utf-8'))
    build = json.loads((AUDIT / 'build_evidence.json').read_text(encoding='utf-8'))
    ndhm = json.loads((AUDIT / 'ndhm_measurement.json').read_text(encoding='utf-8'))
    raw = json.loads((AUDIT / 'sources' / 'purdue_gis_feature_638_cqne_4326.json').read_text(encoding='utf-8'))['features'][0]
    attrs = raw['attributes']
    g = probe['gis_footprint_check']
    footprint_ok = (g['source_feature_id'] == 638 and g['source_ring_unique_vertices'] == g['wall_bottom_vertex_count'] == 54 and g['max_source_vertex_to_wall_nearest_m'] < 0.001)
    transform_ok = (probe['expected_collection_present'] and all(all(abs(v) < 1e-8 for v in o['location'] + o['rotation_euler']) and all(abs(v-1) < 1e-8 for v in o['scale']) for o in probe['objects']))
    native = ndhm['native_height_summary']['quantiles']
    m_if_ft = ndhm['native_height_summary']['if_native_values_are_US_survey_feet_quantile_m']
    vertical_units_declared = not any('not explicitly declared' in s.lower() for s in [ndhm['source']['vertical_unit_limit']])
    portable = (probe['expected_collection_present'] and probe['object_count'] == 7 and all(not o['modifiers'] for o in probe['objects']) and not [i for i in probe['external_images'] if i['filepath']])
    criteria = [
      {'criterion':'Correct identity and source-backed footprint','score':2.0 if footprint_ok else 0.0,'max_score':2.0,'evidence':[
        f"Purdue BuildingShapesZip4 FeatureServer FID {attrs['FID']} names {attrs['BUILDING_N']} (CQNE).",
        f"Independent comparison of {g['source_ring_unique_vertices']} unique raw GIS vertices with the reopened bottom wall ring: maximum nearest-vertex difference {g['max_source_vertex_to_wall_nearest_m']:.8f} m; mean {g['mean_source_vertex_to_wall_nearest_m']:.8f} m.",
        f"Plan bounds are {g['source_bounds'][1][0]-g['source_bounds'][0][0]:.3f} m east-west by {g['source_bounds'][1][1]-g['source_bounds'][0][1]:.3f} m north-south."
      ],'findings':[] if footprint_ok else ['The asset wall ring does not match the raw facility GIS outline.']},
      {'criterion':'Position, orientation, and scale/dimensions','score':2.0 if transform_ok else 0.0,'max_score':2.0,'evidence':[
        'Reopened asset uses the expected campus-coordinate massing collection with identity location, rotation, and scale for all seven objects.',
        'The GIS outline is transformed by the repository documented local latitude/longitude approximation and the reopened structural ring agrees at sub-millimeter precision.',
        f"World bounds include the modeled roof overhang: {probe['world_dimensions_m'][0]:.3f} x {probe['world_dimensions_m'][1]:.3f} x {probe['world_dimensions_m'][2]:.3f} m."
      ],'findings':['The repository geographic conversion is approximate and is not a surveyed CRS.']},
      {'criterion':'Evidence-backed height, floors, and roof form','score':1.5,'max_score':2.0,'evidence':[
        f"Purdue GIS records CountOfFLO={attrs['CountOfFLO']} and the asset renders five facade levels.",
        f"The 2013 5-ft NDHM analysis has {ndhm['mask']['pixels_inside_footprint']} footprint cells; p90/p95 are {native['90']:.3f}/{native['95']:.3f} native units. If those values are US survey feet, they convert to {m_if_ft['90']:.3f}/{m_if_ft['95']:.3f} m, bracketing the modeled 16.0 m peak.",
        'Cross-building NDHM bands show a central high region and the Purdue complex aerial depicts pitched roofs; these support a broad gable interpretation, not a surveyed exact roof profile.'
      ],'findings':[
        'The NDHM GeoTIFF declares horizontal CRS units of US survey feet but does not explicitly declare raster vertical units. Therefore 16.0 m is conditional on native values also being feet, not a verified height.',
        'The five-floor count is an official GIS field; eave elevation, ridge elevation, and pitch remain estimates.'
      ]},
      {'criterion':'Facade, entrances, and distinctive architecture','score':0.5,'max_score':2.0,'evidence':[
        'The Purdue oblique aerial supports broad Cary brick, pitched-roof, and repeated-window character, but it shows the quad collectively and does not isolate CQNE.',
        'The 1950s Purdue Archives image is of Cary Hall generally and is not identified as this northeast building; it provides historical complex context only.',
        'The candidate has five rows of repeated windows and horizontal courses, all appropriately described as schematic/visual estimates.'
      ],'findings':[
        'No CQNE-specific elevation or clear facade photograph was supplied; exact window count/spacing, entrance location, facade materials/trim, and distinctive details are not verified.',
        'Appearance and complex-wide imagery alone do not establish the details of this individual facade.'
      ]},
      {'criterion':'Modular export, portability, and complete evidence','score':2.0 if portable else 0.0,'max_score':2.0,'evidence':[
        f"Fresh Blender {probe['blender_version']} reopen found the expected named asset collection in scene {probe['active_scene']} with {probe['object_count']} mesh objects.",
        'All inspected objects have identity transforms and no modifiers; there are no external image dependencies.',
        'Building evidence includes the raw Purdue GIS snapshot, official Purdue housing page and imagery, original NDHM tile, native measurement summary, build script, reopen validation, and rendered previews.'
      ],'findings':[] if portable else ['Collection, dependency, or modifier validation failed.']}
    ]
    score = round(sum(c['score'] for c in criteria),2)
    findings = [f"{'PASS' if score >= 8 else 'FAIL'} at {score:.2f}/10; minimum passing score is 8/10.",
      'The conditional NDHM unit interpretation is explicitly retained as an uncertainty.',
      'Do not claim an exact CQNE facade, entrance, or measured height from this grade.']
    return {'building_id':ID,'asset':str(ASSET.relative_to(ROOT)).replace('\\','/'),'grade_version':'independent R2','score':score,'max_score':10,'passing_threshold':8,'criteria':criteria,'evidence':[
      f'audit/{ID}/build_evidence.json',f'audit/{ID}/ndhm_measurement.json',f'audit/{ID}/sources/purdue_gis_feature_638_cqne_4326.json',f'audit/{ID}/sources/indiana_2013_ndhm_tile_29951885.tif',f'audit/{ID}/sources/purdue_housing_cary_aerial.jpg',f'audit/{ID}/sources/purdue_archives_cary_quad_1950s.jpg','audit/massing_cary_quadrangle_northeast_cqne_independent_grade_r2/blender_probe.json','audit/massing_cary_quadrangle_northeast_cqne_independent_grade_r2/independent_reopen_preview.png'], 'findings':findings}

if __name__ == '__main__':
    result=evaluate()
    (HERE/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))

