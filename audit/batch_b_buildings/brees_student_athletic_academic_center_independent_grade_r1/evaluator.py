from pathlib import Path
import hashlib, json

ROOT = Path(__file__).resolve().parents[3]
ASSET = ROOT / 'modular/buildings/brees_student_athletic_academic_center.blend'
EVIDENCE = ROOT / 'audit/batch_b_buildings/brees_student_athletic_academic_center_evidence.json'
FRESH = ROOT / 'audit/batch_b_buildings/brees_student_athletic_academic_center_fresh_open.json'
MANIFEST = ROOT / 'modular/manifest.json'
OUT = Path(__file__).with_name('result.json')
EXPECTED_SHA = 'af9dbcb8ae17d42f827799bf8814d1c0af1e793f6915da9ce8be59081c40ce96'


def evaluate():
    sha = hashlib.sha256(ASSET.read_bytes()).hexdigest()
    e = json.loads(EVIDENCE.read_text(encoding='utf-8'))
    fresh = json.loads(FRESH.read_text(encoding='utf-8'))
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    m = next(x for x in manifest['assets'] if x['id'] == 'brees_student_athletic_academic_center')
    expected_origin = tuple(e['official_gis']['campus_placement_origin_xy_m'])
    manifest_origin = tuple(m['placement_origin_xy_m'])
    reopened_origin = tuple(fresh['placement_origin_xy_m'])
    origin_error_m = sum((a-b)**2 for a,b in zip(expected_origin, reopened_origin))**0.5
    stable_asset = (sha == EXPECTED_SHA and fresh['asset_sha256'] == EXPECTED_SHA
                    and fresh['status'] == 'PASS'
                    and fresh['stable_collection'] == 'Asset_brees_student_athletic_academic_center'
                    and manifest_origin == expected_origin and reopened_origin == expected_origin)
    no_external_textures = not fresh['external_image_texture_paths']
    scores = [1.7, 1.4, 1.3, 1.2, 1.9]
    criteria = [
      {'name':'Identity and source-backed footprint','score':scores[0],'max_score':2,
       'evidence':'Official Purdue ArcGIS FID 255 names Drew & Brittany Brees Student Athletic Center and the raw WGS84 feature is preserved. The described 26-vertex outline drives the shell. I confirmed the stable asset and FID fields in the saved-file verification. The source service supplies no survey date/tolerance, and I did not independently recover a surveyed wall-line comparison.',
       'findings':'Identity is well supported; the footprint source is authoritative but its wall-versus-roof boundary and accuracy tolerance are unknown.'},
      {'name':'Position, orientation and dimensions','score':scores[1],'max_score':2,
       'evidence':f'The reopened asset origin is {list(reopened_origin)} and equals both the manifest and GIS-derived evidence origin; horizontal origin error is {origin_error_m:.6f} m. The shell is retained in the local frame. One official oblique facade photo supports broad front direction, but it does not establish surveyed bearing or exact dimensions.',
       'findings':'Placement/origin is verified to the project transform. Front bearing and feature orientation remain photo-interpreted, and the broad local bounds alone do not prove each structural dimension.'},
      {'name':'Height, floors and roof','score':scores[2],'max_score':2,
       'evidence':'Purdue GIS reports two levels; the model represents two above-grade floors and an approximately 11.5 m envelope with a flat roof. The legacy extrusion field is undocumented and the evidence correctly labels height as estimated. The reference photo is consistent with a low, flat-roofed two-storey academic wing.',
       'findings':'Floor count and broad roof form have support, but absolute height and roof elevations remain estimates; no measured section or LiDAR comparison was supplied.'},
      {'name':'Facade, entrances and distinctive architecture','score':scores[3],'max_score':2,
       'evidence':'The rendered model has red brick, a dark horizontal upper band, narrow dark windows, an ivy/banner bay, gold lettering, and a schematic entry. These features correspond to the cited official event photograph. In direct visual comparison, the reference has a substantially more prominent deep charcoal ribbed band, a large photo-composite banner with imagery, and much taller/slender window strips. The model substitutes text on a dark rectangle for the recognizable banner graphic; its openings read as short isolated panes in the supplied front render.',
       'findings':'The material palette and broad composition are improved and source-based, but some of the most recognizable elevation details remain simplified or proportionally weak. Improve the banner imagery, increase the depth/height and horizontal rib definition of the dark upper cladding, and make the window strips match the photo proportions before claiming close facade fidelity.'},
      {'name':'Modular export, portability and evidence','score':scores[4],'max_score':2,
       'evidence':f'Fresh-open PASS for the exact saved SHA {sha}; expected stable collection is present; the manifest/evidence/reopened origin all agree; 105 objects/102 meshes and 13 node materials are reported; no external image paths were found. Evidence preserves the official GIS response, renovation-plan PDF/page, and official photo; schematic interior limitations are stated.',
       'findings':'Packaging and evidence are strong. The evaluation does not treat object density or the builder’s own packaging verifier as evidence of architectural accuracy.'}
    ]
    score = round(sum(c['score'] for c in criteria), 2)
    return {
      'building':'Drew and Brittany Brees Student Athletic Academic Center',
      'asset':'modular/buildings/brees_student_athletic_academic_center.blend',
      'asset_sha256_evaluated':sha,
      'expected_sha256':EXPECTED_SHA,
      'independent_grade':True,
      'score':score,
      'max_score':10,
      'pass_threshold':8,
      'passed':score >= 8 and stable_asset,
      'criteria':criteria,
      'evidence':{
        'fresh_open_verification':'audit/batch_b_buildings/brees_student_athletic_academic_center_fresh_open.json',
        'building_evidence':'audit/batch_b_buildings/brees_student_athletic_academic_center_evidence.json',
        'official_gis_snapshot':'audit/batch_b_buildings/brees_student_athletic_academic_center_gis_feature.json',
        'renovation_plan':'audit/batch_b_buildings/brees_student_athletic_academic_center_2018_renovation_plan.pdf',
        'visual_reference':'audit/batch_b_buildings/brees_student_athletic_academic_center_reference_2026-10-27.jpg',
        'renders':['audit/batch_b_buildings/brees_student_athletic_academic_center_front.png','audit/batch_b_buildings/brees_student_athletic_academic_center_oblique.png','audit/batch_b_buildings/brees_student_athletic_academic_center_top.png','audit/batch_b_buildings/brees_student_athletic_academic_center_fresh_open.png'],
        'manifest_origin_xy_m':list(manifest_origin),
        'reopened_origin_xy_m':list(reopened_origin),
        'origin_error_m':origin_error_m,
        'fresh_open_status':fresh['status'],
        'fresh_open_errors':fresh['errors'],
        'external_image_texture_paths':fresh['external_image_texture_paths'],
        'rubric_total_matches':round(score,2) == round(sum(c['score'] for c in criteria),2)
      },
      'findings':[
        'The asset is safely packaged and correctly anchored to the recorded local placement, but that does not compensate for the remaining facade mismatch.',
        'The exterior reference photo has a large inset photographic champions banner; the model currently renders only a dark text plaque.',
        'The source photo shows long, narrow window strips and a broad ribbed charcoal upper facade band; these proportions are not yet convincing in the front render.',
        'Interior room placement is schematic because the renovation plan is not georegistered; it should remain labeled schematic.'
      ]
    }

result = evaluate()
assert result['asset_sha256_evaluated'] == EXPECTED_SHA, 'asset changed while grading'
assert result['evidence']['fresh_open_status'] == 'PASS'
assert result['evidence']['rubric_total_matches']
OUT.write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps({'score':result['score'],'passed':result['passed'],'sha256':result['asset_sha256_evaluated'],'output':str(OUT)},indent=2))
