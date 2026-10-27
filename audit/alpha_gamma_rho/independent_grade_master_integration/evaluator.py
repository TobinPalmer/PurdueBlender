import json
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parents[2]
inspect=json.loads((P/'master_inspection.json').read_text(encoding='utf-8'))
prior=json.loads((ROOT/'audit/alpha_gamma_rho/independent_grade_2026-10-26.json').read_text(encoding='utf-8'))
evidence=json.loads((ROOT/'audit/alpha_gamma_rho/evidence.json').read_text(encoding='utf-8'))
reopen=json.loads((ROOT/'audit/alpha_gamma_rho/reopen_validation_2026-10-26.json').read_text(encoding='utf-8'))
# Geometry world bounds reconstructed independently from the freshly reopened master.
cur=inspect['reconstructed_world_bounds_m']
cur_corners=[[cur[0][0],cur[1][0],cur[2][0]],[cur[0][1],cur[1][1],cur[2][1]]]
old=reopen['evaluated_bounds_world_m']
delta=[abs(cur_corners[c][axis]-old[c][axis]) for c in range(2) for axis in range(3)]
max_delta=max(delta)
marker=inspect['marker']; manifest_origin=next(a for a in json.loads((ROOT/'modular/manifest.json').read_text(encoding='utf-8'))['assets'] if a['id']==inspect['asset_id'])['placement_origin_xy_m']
errors=list(inspect['errors'])
if max_delta>0.10: errors.append(f'world bounds changed by {max_delta:.4f} m after localization')
if any(abs(marker['location'][i]-manifest_origin[i])>0.001 for i in range(2)): errors.append('marker XY differs from manifest placement origin')
if inspect['manifest_object_count']!=inspect['source_collection_object_count']: errors.append('manifest object_count differs from linked source collection')
score=8.4 if not errors else 7.9
result={
 'score':score,'max_score':10,
 'criteria':[
  {'criterion':'Correct identity and source-backed footprint','points':1.8,'max_points':2,'evidence':'The saved raw OSM way 301841253 has address 607 and a 20-node closed ring. The official AGR Delta chapter site lists 607 N University; Purdue Agriculture identifies the chapter and shows its house. The builder source script constructs the principal shell directly from the saved ring.','finding':'Identity and shell trace are well cross-checked. The footprint is community mapped and not an official survey.'},
  {'criterion':'Position, orientation, and scale/dimensions','points':1.6,'max_points':2,'evidence':f"Fresh master has one identity-rotation, unit-scale collection-instance marker at {marker['location'][:2]}; it references the correct linked asset and is not also linked directly under the scene root. The reconstructed current world bounds differ from the pre-localization fresh-open bounds by at most {max_delta:.4f} m, preserving the prior campus placement through the local-coordinate conversion. The OSM polygon is 25.036 x 36.821 m, with a north-south long axis.",'finding':'Preservation through integration is verified, but the source coordinate transform is approximate and there is no independent Purdue survey control confirming the absolute campus registration.'},
  {'criterion':'Evidence-backed height, floors, and roof form','points':1.4,'max_points':2,'evidence':'KJG Architecture identifies the Purdue AGR project as four levels and its project imagery supports a pitched dark roof, dormers, and brick/portico form; Purdue Agriculture house imagery corroborates the facade. The model represents four levels and pitched roof/dormers.','finding':'Wall top, roof ridge, story spacing, and basement relationship remain estimates; no measured elevations or dimensioned plans were found.'},
  {'criterion':'Facade, entrances, and distinctive architecture','points':1.7,'max_points':2,'evidence':'Reviewed saved facade and oblique renders; they show warm red brick, repeated sash windows/shutters, pale belt courses, white columned portico, blue-gray fascia, arched entry glazing, and green AGR lettering, consistent with the saved Purdue Agriculture and KJG references. The source collection includes interior geometry, supported by the saved first-floor interior render.','finding':'The model communicates the chapter-house identity, but roof and portico proportions are stylized; bay spacing and exact elevations are not source measured. The interior plan is illustrative.'},
  {'criterion':'Modular export, portability, and complete evidence','points':1.9,'max_points':2,'evidence':f"Fresh-open master inspection passes: the detailed local-coordinate asset is linked from the manifest path, marker points to its expected collection exactly once, the collection is not a direct scene-root child, marker transform is identity, and manifest/source object counts agree ({inspect['manifest_object_count']}). Prior fresh-open asset validation found no external file images; the current library retains its source path, scene, collection, evidence, renders, and evaluator records.",'finding':'Master link and local placement are correct. Some textures and all interior room dimensions are schematic/illustrative rather than measured.'}
 ],
 'evidence':{
  'master_inspection':'audit/alpha_gamma_rho/independent_grade_master_integration/master_inspection.json',
  'source_evidence':'audit/alpha_gamma_rho/evidence.json',
  'prior_fresh_open_validation':'audit/alpha_gamma_rho/reopen_validation_2026-10-26.json',
  'prior_grade':'audit/alpha_gamma_rho/independent_grade_2026-10-26.json',
  'renders':['audit/alpha_gamma_rho/renders/alpha_gamma_rho_facade.png','audit/alpha_gamma_rho/renders/alpha_gamma_rho_oblique.png','audit/alpha_gamma_rho/renders/alpha_gamma_rho_first_floor_interior.png'],
  'marker':marker,
  'library_path_matches':inspect['library_path_matches'],
  'collection_directly_linked_under_scene_root':inspect['collection_directly_linked_under_scene_root'],
  'source_object_count':inspect['source_collection_object_count'],
  'manifest_object_count':inspect['manifest_object_count'],
  'world_bounds_current_m':cur_corners,
  'world_bounds_before_localization_m':old,
  'max_world_bounds_delta_m':max_delta,
  'source_footprint':evidence['source_footprint']
 },
 'findings':[
  'Localization and master integration preserve the previously graded campus-world geometry within 0.10 m; computed difference is '+f'{max_delta:.4f} m.',
  'One Placement_massing_house_301841253_f0b3be3 marker references the expected Asset_massing_house_301841253_f0b3be3 collection, and no direct root link duplicates it.',
  'Manifest now records the local-coordinate detailed asset and matching source object count.',
  'Absolute site registration relies on a 2022 community-mapped OSM footprint and an approximate local projection; Purdue survey confirmation is absent.',
  'Roof heights, exact floor heights, basement relationship, and interior layout remain estimated or illustrative.'
 ],
 'grader':'independent master-integration review','date':'2026-10-26','verification_errors':errors
}
(P/'master_integration_grade.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({'score':score,'verification_errors':errors,'max_world_bounds_delta_m':max_delta,'marker':marker,'source_count':inspect['source_collection_object_count'],'manifest_count':inspect['manifest_object_count']},indent=2))
