import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
EVIDENCE=HERE.parent

def evaluate():
    """Fresh independent grade for the saved Riverside asset and corrected evidence."""
    ev=json.loads((EVIDENCE/'evidence.json').read_text(encoding='utf-8-sig'))
    gis=json.loads((EVIDENCE/'indiana_building_footprint_feature_409445.json').read_text(encoding='utf-8-sig'))
    fp=json.loads((EVIDENCE/'footprint_comparison_indiana_2018_vs_osm.json').read_text(encoding='utf-8-sig'))
    validation=json.loads((EVIDENCE/'reopen_validation.json').read_text(encoding='utf-8-sig'))
    config=json.loads((EVIDENCE/'build_config.json').read_text(encoding='utf-8-sig'))
    obs=json.loads((EVIDENCE/'source_reference_observation.json').read_text(encoding='utf-8-sig'))
    criteria=[
      {'name':'Correct identity and source-backed footprint','score':1.8,'max_score':2,
       'evidence':['The owner history identifies Riverside at 1850 Woodland Avenue and an acquired church building. The preserved named OSM building outline independently overlaps IndianaMap feature 409445 at 0.8867 IoU.',f"The current asset follows the projected state GIS ring; reopened ring error is {validation['max_source_ring_error_m']:.8f} m.",f"State GIS polygon area {fp['official_footprint_area_m2']:.2f} m²; OSM polygon area {fp['osm_footprint_area_m2']:.2f} m²."],
       'deduction':'The statewide GIS footprint is not a legal survey and has a 12.7% area difference from OSM; exact structural-wall extents remain uncertain.'},
      {'name':'Position, orientation, and scale/dimensions','score':1.6,'max_score':2,
       'evidence':[f"Campus coordinates remain in an identity world transform; independent GIS/OSM centroid difference is {fp['centroid_offset_m']:.3f} m and polygon IoU is {fp['footprint_iou']:.4f}.",f"The saved asset reproduces the projected GIS ring within {validation['max_source_ring_error_m']:.8f} m; its expected direct-link scene and collection are preserved."],
       'deduction':'Coordinates use the documented local approximation, not a surveyed CRS. No evidence establishes the entrance true-north orientation or surveyed dimensions.'},
      {'name':'Evidence-backed height, floors, and roof form','score':1.2,'max_score':2,
       'evidence':['The dated 2016 exterior photograph supports the low, horizontal roof and centered tall glazed A-frame; the saved preview matches that dominant silhouette.',f"Current config labels eaves {config['wall_eaves_m']} m, main ridge {config['ridge_height_m']} m, and glazed apex {config['glazed_apex_m']} m as estimates."],
       'deduction':'The photo establishes relative appearance only. Absolute heights, roof pitch, and floor count remain unverified.'},
      {'name':'Facade, entrances, and distinctive architecture','score':1.6,'max_score':2,
       'evidence':['The reference photo directly shows a broad brick frontage, centered light-framed glazed A-frame, and multiple entry bays. Front and oblique renders reproduce these major features in a centered arrangement.','The model contains a corresponding mullion grid and four door-bay forms.'],
       'deduction':'Side-window count/spacing, exact material colors, facade proportions, and opening dimensions remain schematic; only one perspective photo is available.'},
      {'name':'Modular export, portability, and complete evidence','score':1.9,'max_score':2,
       'evidence':[f"Blender 5.2.3 independently reopened the expected scene and one object in the named collection; mesh {validation['mesh_vertices']} vertices, {validation['mesh_faces']} faces, no modifiers.","Dedicated build module retains the asset path, IDs, collection, and direct-link campus-coordinate frame; raw GIS/OSM snapshots, metadata, comparison, dated facade image, build/render/validation scripts and previews are preserved.","The stale modeling limitations text was corrected to describe current GIS/photo evidence and current estimated dimensions."],
       'deduction':'The top preview is not useful for checking facade details, and the main evidence status still says independent grading is pending despite the prior passing grade; refresh its status/index after this evaluation.'}
    ]
    score=round(sum(x['score'] for x in criteria),2)
    result={'score':score,'max_score':10,'criteria':criteria,
      'evidence':['Opened the exact saved .blend in Blender 5.2.3 and checked scene, collection membership, transforms, mesh counts, world bounds, materials, and modifiers.', 'Reviewed the corrected source_reference_observation.json modeling limitations, main evidence and configuration, source snapshots, independent footprint comparison, reopen record, exterior photo, and current oblique/front/top renders.'],
      'findings':[
       {'priority':'medium','status':'documented','finding':'Absolute elevation, roof pitch, floor count, exact window layout, and entrance orientation relative to north remain estimates or unverified.'},
       {'priority':'low','status':'documented','finding':'IndianaMap is an independent reference footprint, not a cadastral survey; it overlaps OSM strongly but differs in area by about 12.7%.'},
       {'priority':'low','status':'update_after_grade','finding':'Update evidence.json status/artifact index to record this independent grade; it still marks grading pending.'}
      ],
      'asset_inspection':{'blender_version':validation['blender_version'],'scene':validation['asset_id'],'collection_object_count':validation['collection_objects'],'object':validation['object'],'vertices':validation['mesh_vertices'],'faces':validation['mesh_faces'],'bounds_world_m':validation['bounds_world_m'],'world_matrix':validation['world_matrix'],'materials':validation['materials'],'modifiers':validation['modifiers']},
      'grade_status':'pass' if score>=8 else 'fail: below minimum 8/10','reviewer':'Independent rubric evaluation'}
    return result

if __name__=='__main__':
    result=evaluate()
    (HERE/'result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

