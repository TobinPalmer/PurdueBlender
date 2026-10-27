from pathlib import Path
import hashlib, json
ROOT=Path(__file__).resolve().parents[3]
ASSET=ROOT/'modular/buildings/convergence_center.blend'
EVIDENCE=ROOT/'audit/convergence_center_evidence.json'
FRESH=ROOT/'audit/convergence_center/fresh_open_validation.json'
PROBE=Path(__file__).with_name('direct_asset_probe.json')
GEOM=Path(__file__).with_name('direct_geometry_probe.json')
MANIFEST=ROOT/'modular/manifest.json'
EXPECTED='304515ac91cedeef967349e120c87ae387071806845d129a97128c0e1c231928'
OUT=Path(__file__).with_name('result.json')

def evaluate():
    sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()
    ev=json.loads(EVIDENCE.read_text(encoding='utf-8'))
    fresh=json.loads(FRESH.read_text(encoding='utf-8'))
    probe=json.loads(PROBE.read_text(encoding='utf-8'))
    geom=json.loads(GEOM.read_text(encoding='utf-8'))
    manifest=json.loads(MANIFEST.read_text(encoding='utf-8'))
    m=next(x for x in manifest['assets'] if x['id']=='convergence_center')
    expected_origin=ev['coordinate_frame']['local_origin_xy_m']
    fresh_origin=fresh['placement_origin_xy_m']
    manifest_origin=m['placement_origin_xy_m']
    origin_ok=expected_origin==fresh_origin==manifest_origin
    sha_ok=sha==EXPECTED and fresh['asset_sha256']==EXPECTED and probe['sha256']==EXPECTED and fresh['status']=='PASS'
    texture_ok=not fresh['external_image_paths'] and not geom['missing_texture_nodes'] and not geom['unresolved_external_image_paths']
    rubric=[
      {'category':'Identity and site placement','score':1.9,'max_score':2,
       'evidence':f'Official Purdue GIS feature FID 946 is named Convergence (CONV), with 101 Foundry Drive corroborated by Purdue Innovates. The evidence identifies the west/Foundry frontage from sources and Google Maps context. Saved asset metadata identifies FID 946 and stable ID convergence_center. The campus/local origin {expected_origin} matches the manifest and independent fresh-open report exactly.',
       'limitations':'I did not independently inspect master neighbors or Google Street View exterior coverage; facade bearing and the exact door bay are inferred, and the source explicitly states the selected Street View point does not provide usable exterior imagery.'},
      {'category':'Footprint and form','score':1.9,'max_score':2,
       'evidence':f'I opened the exact saved .blend and compared the 12-edge ground-plate boundary with official FID 946 GeoJSON using the documented project transform. Maximum source-to-model boundary deviation is {geom["max_source_to_asset_boundary_deviation_m"]:.8f} m and model-to-source deviation is {geom["max_asset_to_source_boundary_deviation_m"]:.8f} m. The source-backed stepped footprint is retained. Five floors are supported by Purdue/CSO sources; the flat roof is visible in the architect photos.',
       'limitations':'The GIS feature is not a certified wall survey. The 20.45 m main roof height and floor-to-floor heights are estimates; the additional modeled bounds include parapet/roof detail.'},
      {'category':'Facade, materials and source fidelity','score':1.5,'max_score':2,
       'evidence':'Official Purdue and CSO as-built imagery supports pale vertically ribbed metal cladding, a repeated five-floor punched window pattern, a large glazed ground floor, broad white entry portal/canopy, and freestanding branded monument. The model includes these elements, red brick piers, dark spandrels, connected procedural materials, portal and separate monument sign. Roof form and general building proportions track the photo.',
       'limitations':'In the front/oblique model render, upper windows read smaller and squarer than the broad rectangular bays in the as-built photograph; the entry portal/canopy, glazing rhythm, monument and material contrast are simplified. Plaza paving, site planting, cars and adjacent context are mostly absent, so the exterior is a clean building asset rather than a fully matched streetscape.'},
      {'category':'Interior','score':1.4,'max_score':2,
       'evidence':'Direct inspection of the saved collection found a double-height lobby floor, reception counter, feature wall/wordmark, partial mezzanine and guardrail, lounge seats, tables, and planters. These elements correspond to CSO architect interior photographs showing an atrium lobby, desk, mezzanine, seating and planting. The asset and evidence label this area schematic.',
       'limitations':'No complete georegistered plan was available. My independent interior camera render did not show a particularly clear or convincing interior composition through the facade; the room layout and furnishings are a small photo-guided vignette and should not be read as a factual floor plan.'},
      {'category':'Portability and fresh-open validation','score':1.9,'max_score':2,
       'evidence':f'Blender 5.2.3 independently opened the saved file at exact SHA {sha}. The `Asset_convergence_center` collection and local-coordinate metadata are present; fresh-open validation passes with 764 objects, 760 meshes, 12 materials, and no external image dependencies. Direct inspection found no empty image nodes or unresolved external image paths; all materials use procedural or built-in nodes.',
       'limitations':'The targeted sign/canopy intersection check covers only that pair and is not a complete collision or geometry-health audit.'}
    ]
    score=round(sum(x['score'] for x in rubric),2)
    return {'building':'Convergence Center for Innovation and Collaboration','asset':'modular/buildings/convergence_center.blend','asset_sha256_evaluated':sha,'expected_sha256':EXPECTED,'independent_grade':True,'score':score,'max_score':10,'pass_threshold':8,'passed':score>=8 and sha_ok and origin_ok and texture_ok,'criteria':rubric,'evidence':{'evidence_record':'audit/convergence_center_evidence.json','fresh_open_report':'audit/convergence_center/fresh_open_validation.json','direct_saved_asset_probe':'audit/convergence_center/independent_grade_r1/direct_asset_probe.json','direct_GIS_footprint_comparison':'audit/convergence_center/independent_grade_r1/direct_geometry_probe.json','official_GIS_native':'audit/convergence_gis_feature_946_native.json','official_GIS_GeoJSON':'audit/convergence_gis_feature_946.geojson','Purdue_2020_as_built':'audit/convergence_center/official_purdue_2020_photo.jpg','Purdue_2018_design':'audit/convergence_center/official_purdue_2018_rendering.jpg','CSO_built_exterior':'audit/convergence_center/official_cso_convergence_03.jpg','CSO_lobby_photo':'audit/convergence_center/official_cso_convergence_02.jpg','renders':['audit/convergence_center/fresh_open_preview.png','audit/convergence_center_west_elevation.png','audit/convergence_center_entry_detail.png','audit/convergence_center_lobby_detail.png','audit/convergence_center_roof_plan.png','audit/convergence_center/independent_grade_r1/interior_detail_independent.png'],'origin_matches_evidence_manifest_fresh_open':origin_ok,'origin_xy_m':expected_origin,'max_source_to_asset_boundary_deviation_m':geom['max_source_to_asset_boundary_deviation_m'],'max_asset_to_source_boundary_deviation_m':geom['max_asset_to_source_boundary_deviation_m'],'sha_and_fresh_open_pass':sha_ok,'textures_portable':texture_ok,'schematic_lobby_object_count':geom['lobby_object_count']},'findings':['The GIS identity and 12-edge structural outline are unusually well supported and directly compared against the saved model.','The massing, five-floor count, flat roof, pale vertical cladding, punched glazing and glazed portal are source-backed; dimensions above the plan and facade module remain estimates.','Interior elements are present and align in character with CSO photographs but are explicitly schematic and not georegistered.','The as-built facade image shows larger rectangular upper window bays and a more developed street/plaza foreground than the model currently conveys.']}

result=evaluate()
assert result['asset_sha256_evaluated']==EXPECTED, 'asset changed during grading'
assert result['evidence']['origin_matches_evidence_manifest_fresh_open']
assert result['evidence']['sha_and_fresh_open_pass']
assert result['evidence']['textures_portable']
assert result['score']==round(sum(x['score'] for x in result['criteria']),2)
OUT.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({'score':result['score'],'passed':result['passed'],'sha256':result['asset_sha256_evaluated'],'output':str(OUT)},indent=2))
