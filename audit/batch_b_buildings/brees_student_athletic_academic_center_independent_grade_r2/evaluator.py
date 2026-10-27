from pathlib import Path
import hashlib, json
ROOT=Path(__file__).resolve().parents[3]
ASSET=ROOT/'modular/buildings/brees_student_athletic_academic_center.blend'
EVIDENCE=ROOT/'audit/batch_b_buildings/brees_student_athletic_academic_center_evidence.json'
FRESH=ROOT/'audit/batch_b_buildings/brees_student_athletic_academic_center_fresh_open.json'
PROBE=Path(__file__).with_name('direct_asset_probe.json')
MANIFEST=ROOT/'modular/manifest.json'
EXPECTED_SHA='7e5f8b8c953911749e2b9f13453b9f6813657b45f4bfb55934c42bc5a5c4fc44'
OUT=Path(__file__).with_name('result.json')

def evaluate():
    sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()
    evidence=json.loads(EVIDENCE.read_text(encoding='utf-8'))
    fresh=json.loads(FRESH.read_text(encoding='utf-8'))
    direct=json.loads(PROBE.read_text(encoding='utf-8'))
    manifest=json.loads(MANIFEST.read_text(encoding='utf-8'))
    entry=next(x for x in manifest['assets'] if x['id']=='brees_student_athletic_academic_center')
    origin=evidence['official_gis']['campus_placement_origin_xy_m']
    manifest_origin=entry['placement_origin_xy_m']
    reopened_origin=fresh['placement_origin_xy_m']
    source_error=direct['max_source_to_model_edge_error_m']
    reverse_error=direct['max_model_to_source_edge_error_m']
    packed=all(x['packed'] for x in direct['packed_images']) and all(x['packed'] for x in direct['image_materials'])
    fresh_ok=(sha==EXPECTED_SHA and fresh['asset_sha256']==EXPECTED_SHA and fresh['status']=='PASS'
              and direct['sha256']==EXPECTED_SHA and direct['stable_collection']=='Asset_brees_student_athletic_academic_center'
              and origin==manifest_origin==reopened_origin and packed)
    criteria=[
      {'name':'Identity and source-backed footprint','score':1.9,'max_score':2,
       'evidence':f'Official Purdue GIS FID 255 names Drew & Brittany Brees Student Athletic Center. I opened the saved asset and compared its 26-edge structural base boundary with the raw WGS84 source ring under the documented project transform: maximum source-to-model boundary deviation {source_error:.8f} m and model-to-source deviation {reverse_error:.8f} m. The asset retains the FID 255 custom property.',
       'findings':'Identity and geometric outline match are strong. Purdue supplies no survey tolerance or source date, and the feature could trace roof edge rather than surveyed wall line.'},
      {'name':'Position, orientation and dimensions','score':1.7,'max_score':2,
       'evidence':f'The exact project origin {origin} is identical in evidence, manifest and reopened collection metadata (0 m discrepancy). GIS ring and structural shell are the same size/shape within the comparison above. The reference photo supports a facade orientation, though there is no independent survey bearing or dimension set.',
       'findings':'Origin and footprint dimensions are verified against this local GIS transform. Facade bearing remains inferred from imagery and the north-side entry is plan-interpreted.'},
      {'name':'Height, floors and roof','score':1.3,'max_score':2,
       'evidence':'Purdue GIS lists two levels; the current shell spans 11.5 m and the model uses two above-grade levels with a low flat roof, broadly consistent with the official image. The GIS extrusion value has no documented unit/datum and the evidence labels height as estimated.',
       'findings':'The floor count and roof silhouette are plausible, but no reliable elevation, measured roof height, or section source verifies the 11.5 m height.'},
      {'name':'Facade, entrances and distinctive architecture','score':1.7,'max_score':2,
       'evidence':f'The independently inspected front and banner-detail renders now show the photo-supported red brick, broad continuous dark ribbed band, ivy, gold two-line identification, and a custom athlete-collage/P banner graphic. Direct Blender inspection found 52 facade glazing quads, each 2.35 m tall; this matches the long slit-window proportion in the reference. The dark backing is a continuous 26-face perimeter layer with 312 raised rib faces.',
       'findings':'R2 resolves the prominent R1 facade gaps. The banner artwork is an original stylized interpretation rather than a pixel match, and the exact north-side entrance surround and facade bearing remain uncertain.'},
      {'name':'Modular export, portability and evidence','score':1.9,'max_score':2,
       'evidence':f'Blender 5.2.3 opened the exact saved SHA {sha} in a separate background process. The stable `Asset_brees_student_athletic_academic_center` collection is present, and fresh-open validation passes. The illustrated banner is packed in the blend; the direct asset probe confirms it is used by its material and packed, with no external image path recorded. The renovation-plan-derived interior objects are consistently prefixed `SCHEMATIC_ONLY_`; GIS, plan, official photo and uncertainty records are preserved.',
       'findings':'Packaging and provenance are strong. The renovation plan cannot be georegistered, so room layout and Holloway court placement remain visual cues, not verified interiors.'}
    ]
    score=round(sum(x['score'] for x in criteria),2)
    return {'building':'Drew and Brittany Brees Student Athletic Academic Center','asset':'modular/buildings/brees_student_athletic_academic_center.blend','asset_sha256_evaluated':sha,'expected_sha256':EXPECTED_SHA,'independent_grade':True,'score':score,'max_score':10,'pass_threshold':8,'passed':score>=8 and fresh_ok,'criteria':criteria,'evidence':{'prior_grade_context':'audit/batch_b_buildings/brees_student_athletic_academic_center_independent_grade_r1/result.json (used only to identify repaired shortcomings; R2 score assessed afresh)','fresh_open_verification':'audit/batch_b_buildings/brees_student_athletic_academic_center_fresh_open.json','direct_saved_asset_probe':'audit/batch_b_buildings/brees_student_athletic_academic_center_independent_grade_r2/direct_asset_probe.json','building_evidence':'audit/batch_b_buildings/brees_student_athletic_academic_center_evidence.json','gis_snapshot':'audit/batch_b_buildings/brees_student_athletic_academic_center_gis_feature.json','renovation_plan':'audit/batch_b_buildings/brees_student_athletic_academic_center_2018_renovation_plan.pdf','photo_reference':'audit/batch_b_buildings/brees_student_athletic_academic_center_reference_2026-10-27.jpg','renders':['audit/batch_b_buildings/brees_student_athletic_academic_center_front.png','audit/batch_b_buildings/brees_student_athletic_academic_center_oblique.png','audit/batch_b_buildings/brees_student_athletic_academic_center_top.png','audit/batch_b_buildings/brees_student_athletic_academic_center_banner_detail.png','audit/batch_b_buildings/brees_student_athletic_academic_center_fresh_open.png'],'source_to_model_edge_error_m':source_error,'model_to_source_edge_error_m':reverse_error,'glazing_heights_m':direct['glazing_face_height_values_m'],'glazing_quad_count':direct['glazing_quads'],'upper_cladding_backing_faces':direct['backing_faces'],'rib_faces':direct['rib_faces'],'packed_banner_asset':packed,'origin_matches_manifest_and_reopened_asset':origin==manifest_origin==reopened_origin,'exact_sha_and_fresh_open_pass':fresh_ok},'findings':['R2 corrects the R1 facade issues: packed custom athlete collage, substantially more prominent continuous ribbed cladding, and tall slit windows now correspond closely to the cited photo.','GIS shell outline matches the official FID 255 ring under the project transform to sub-micrometre edge distance; interpret this as agreement with that feature, not surveyed wall accuracy.','The 11.5 m height is estimated; the model correctly limits its factual story claim to two above-grade levels and states interior layout is schematic.']}

result=evaluate()
assert result['asset_sha256_evaluated']==EXPECTED_SHA, 'asset changed during grading'
assert result['evidence']['exact_sha_and_fresh_open_pass']
assert result['evidence']['origin_matches_manifest_and_reopened_asset']
assert result['evidence']['packed_banner_asset']
assert result['score']==round(sum(x['score'] for x in result['criteria']),2)
OUT.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({'score':result['score'],'passed':result['passed'],'sha256':result['asset_sha256_evaluated'],'output':str(OUT)},indent=2))
