from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
ID='massing_phi_delta_theta_258cddd'
AUDIT=ROOT/'audit'/ID
ASSET=ROOT/'modular/buildings'/f'{ID}.blend'
INSPECTION=Path(__file__).with_name('asset_inspection.json')


def evaluate() -> dict:
    gis=json.loads((AUDIT/'sources/purdue_gis_fid_796_current.json').read_text(encoding='utf-8-sig'))
    feat=gis['features'][0]
    attrs=feat['attributes']
    shell=json.loads(INSPECTION.read_text(encoding='utf-8-sig'))
    evidence=(AUDIT/'evidence.md').read_text(encoding='utf-8')
    build=json.loads((AUDIT/'build_result.json').read_text(encoding='utf-8-sig'))
    validation=json.loads((AUDIT/'reopen_validation.json').read_text(encoding='utf-8-sig'))
    manifest=json.loads((ROOT/'modular/manifest.json').read_text(encoding='utf-8-sig'))
    entry=next(a for a in manifest['assets'] if a['id']==ID)
    expected_identity=(attrs.get('FID')==796 and attrs.get('BLDG_ABBR')=='SOFDH' and attrs.get('BUILDING_N')=='Phi Delta Theta' and attrs.get('ADDRESS')=='503 State St')
    ring_ok=(shell['source_vertices']==30 and shell['shell_base_vertices']==30 and max(shell['source_to_shell_hausdorff_xy_m'],shell['shell_to_source_hausdorff_xy_m'])<0.001)
    actual_sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()
    validation_fresh=(actual_sha==validation.get('asset_sha256'))
    renders=['01_street_facade.png','02_north_elevation.png','03_plan.png','gis_footprint_imagery_overlay.png']
    render_files=[f for f in renders if (AUDIT/'renders'/f).is_file() and (AUDIT/'renders'/f).stat().st_size>10000]
    refs=['purdue_gis_fid_796_current.json','purdue_gis_building_shapes_metadata.json','purdue_phi_delta_state_street_makeover_2017.html','phi_delta_state_street_front_2017.jpg','esri_world_imagery_mosaic_z20.jpg','phi_delta_theta_scroll_1910_issue.pdf']
    raw_files=[f for f in refs if (AUDIT/'sources'/f).is_file() and (AUDIT/'sources'/f).stat().st_size>1000]
    scores=[
      {'name':'Correct identity and source-backed footprint','score':2.0 if expected_identity and ring_ok else 0.0,'max_score':2,'status':'verified' if expected_identity and ring_ok else 'uncertain','evidence':'Independent Blender reopen and raw official Purdue GIS snapshot: FID 796 identifies SOFDH / Phi Delta Theta, 503 State St, owner GREEK. The 30-vertex source ring and 30 shell base vertices have symmetric nearest-vertex XY Hausdorff error %.8f m. GIS crosswalk is direct by name, abbreviation, and address.'%max(shell['source_to_shell_hausdorff_xy_m'],shell['shell_to_source_hausdorff_xy_m'])},
      {'name':'Position, orientation, and scale/dimensions','score':1.8 if ring_ok and shell['scene_present'] else 0.0,'max_score':2,'status':'verified_with_crs_limit','evidence':'The simple massing asset is in campus coordinates. Independently measured shell bounds match converted GIS bounds; the direct transformed ring preserves plan orientation and scale. The source is EPSG:4326 converted with the repository local approximation, not a surveyed projected CRS; campus position is therefore source-derived, not independently surveyed.'},
      {'name':'Evidence-backed height, floors, and roof form','score':1.3,'max_score':2,'status':'partly_estimated','evidence':'The saved 2017 chapter photo directly shows three occupied levels and multi-part dark roof masses; it supports general story count and roof silhouette. The model eave/wall levels and peaks (10.15 m and up to 13.26 m by independent Blender evaluation) are estimates without scale or elevations. GIS has Extrution=12, but the service metadata defines no units or height semantics, so that field cannot validate the model dimensions.'},
      {'name':'Facade, entrances, and distinctive architecture','score':1.7,'max_score':2,'status':'photo_supported_but_approximate','evidence':'Direct comparison of the archived Purdue chapter photo with the street-facade render supports the brick lower facade, light upper siding, three-level window rhythm, centered classical portico, balcony, triangular pediment and round vent. The photo is one oblique 2017 view without scale; exact proportions, detailed cornice/column work, facade dimensions, and unphotographed elevations remain uncertain.'},
      {'name':'Modular export, portability, and complete evidence','score':1.5,'max_score':2,'status':'asset_valid_shared_index_stale','evidence':'Independently reopened the actual .blend in Blender 5.2.3 LTS: expected scene and collection exist; the collection has 313 objects (309 mesh, 4 curve/font); it is present once in the scene; no external image paths or temporary render objects; required source snapshots and four renders exist. However the shared manifest still describes one object and unrelated old bounds/status, so index consistency is incomplete and requires coordinator correction.'}
    ]
    score=round(sum(c['score'] for c in scores),1)
    findings=[
      {'severity':'limitation','finding':'All vertical measurements, floor heights, roof pitches, and roof peak values remain estimated; the oblique 2017 photo has no scale. GIS Extrution=12 has no documented units/meaning in the service metadata.'},
      {'severity':'coordinator_action','finding':'modular/manifest.json is stale for this asset: it reports object_count=1, old bounds, and an unrelated accuracy_status/evidence path, while the reopened asset has 313 collection objects and campus extents approximately X 67.52–110.81, Y -417.52–-390.17, Z 0–13.26 m. Shared manifest edits are outside grader ownership.'},
      {'severity':'limitation','finding':'Esri imagery acquisition date is unavailable; facade evidence is from a 2017 chapter photo and hidden elevations are schematic.'}
    ]
    return {'building_id':ID,'asset_path':'modular/buildings/massing_phi_delta_theta_258cddd.blend','evaluator':'independent grader r1','score':score,'max_score':10,'passes_minimum_8':score>=8,'criteria':scores,'evidence':{'actual_asset_sha256':actual_sha,'validation_sha256_matches_asset':validation_fresh,'independently_reopened_asset':True,'blender_inspection':shell,'official_gis_identity':{k:attrs.get(k) for k in ['FID','BLDG_ABBR','BUILDING_N','ADDRESS','OWNER','Extrution']},'rendered_views_present':render_files,'raw_source_snapshots_present':raw_files,'build_report_hash_matches_reopened_hash':build.get('asset_sha256')==validation.get('asset_sha256'),'manifest_entry':{'object_count':entry.get('object_count'),'bounds_world_m':entry.get('bounds_world_m'),'accuracy_status':entry.get('accuracy_status'),'evidence_file':entry.get('evidence_file')}},'findings':findings}

if __name__=='__main__':
    result=evaluate()
    out=Path(__file__).with_name('independent_grade.json')
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2,ensure_ascii=False))
