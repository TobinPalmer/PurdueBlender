from pathlib import Path
import hashlib, json

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / 'modular' / 'buildings' / 'neil_armstrong_hall.blend'
VALIDATION = Path(__file__).with_name('validation_r12_4.json')
EVIDENCE = Path(__file__).with_name('evidence_r12_1.json')
EXPECTED_SHA = 'fd6a8c7dcbdd21eab4d94ae3a9b38d72d87069260e059996ab689d432927c62e'


def evaluate():
    validation = json.loads(VALIDATION.read_text(encoding='utf-8'))
    evidence = json.loads(EVIDENCE.read_text(encoding='utf-8'))
    actual_sha = hashlib.sha256(ASSET.read_bytes()).hexdigest()
    reopened = bool(validation.get('reopened_in_fresh_blender_process'))
    root_identity = validation.get('root_location') == [0.0, 0.0, 0.0]
    deps_clean = not validation.get('missing_external_images') and not validation.get('external_file_images')
    material_coverage = not validation.get('meshes_without_any_material') and not validation.get('meshes_with_null_material_slot')
    n = validation.get('collection_object_count')
    same_revision = actual_sha == EXPECTED_SHA == validation.get('sha256')

    criteria = [
      {'name':'Correct identity and source-backed footprint','score':1.55,'max_score':2.0,
       'evidence':['Purdue GIS BuildingShapesZip4 feature 642 is identified in evidence_r11.json and the raw feature snapshot is cited.','The red/blue roof/eaves polygon traced in roof_trace_overlay_r12.png follows the 2023 orthophoto roof perimeter and inner roof edge.','The trace is a roof/eaves edge, not the structural wall footprint; no calibrated wall plan or GIS-to-wall overlay is provided.'],
       'findings':['Identity is well supported, and roof plan evidence is materially stronger than R11.','The actual wall footprint/courtyard correspondence remains unverified; traced roof edges cannot establish the wall footprint.']},
      {'name':'Position, orientation, and scale/dimensions','score':1.55,'max_score':2.0,
       'evidence':['The saved library root has identity transform at local origin.','The manifest entry places this local asset at [-109.0, 400.1893310546875] m; the prior R11 read-only master review found the marker aligned with that manifest origin.','The 2023 orthophoto trace gives a registered roof/eaves outline, but source geotag photos have unknown heading/roll and do not verify wall registration or facade stationing.'],
       'findings':['Library/master origin is coherent, but accurate location of architectural walls, orientation, and dimensional fit is not established independently.']},
      {'name':'Evidence-backed height, floors, and roof form','score':1.4,'max_score':2.0,
       'evidence':['Purdue emergency-plan information supports four building levels; prior source review records a 53 ft atrium and a three-story frame from primary/engineering sources.','The aerial supports the roof/eaves footprint; attributed 2016 photos support a folded, wing-like canopy.','Current geometry uses inferred heights and warp; the builder explicitly identifies these as inference and reports visible differences from source views.'],
       'findings':['Building scale/story description is plausible and partly sourced.','The distinctive canopy profile and vertical heights are not dimensionally verified; current renders show a flattened/overbroad folded shell relative to the photo, and a dark triangular inset is acknowledged as unverified interpretation.']},
      {'name':'Facade, entrances, and distinctive architecture','score':1.3,'max_score':2.0,
       'evidence':['The renders show the expected brick masses, glazed entrance/curtain wall, and large cantilevered red-brown canopy; the photo set directly depicts these broad features.','The renders include a courtyard view and cardinal elevations for inspection.'],
       'findings':['Window rhythm and wall segmentation remain generic and are not registered against measured elevations.','The source/render comparison shows a major difference in canopy profile and proportions; the courtyard render has an unexplained opaque dark-blue foreground/panel obstruction that masks the facade.','The entrance/canopy composition is recognizable but still approximate.']},
      {'name':'Modular export, portability, and complete evidence','score':1.8,'max_score':2.0,
       'evidence':[f'Fresh Blender 5.2.3 reopen validation reports {n} collection objects and {validation.get("mesh_object_count")} meshes, identity root, and no materialless/null-material meshes.','No external image dependencies or missing image paths are reported.','Evidence includes attribution/source URLs, raw GIS/orthophoto references, geotagged comparative renders, top registered roof view, and explicit uncertainty.','Actual SHA matches expected revision: '+str(same_revision)+'.'],
       'findings':['Export and portability checks are strong.','Evidence is extensive but does not include a dimensioned public roof/elevation plan or verified wall registration.']}
    ]
    score = round(sum(c['score'] for c in criteria), 2)
    findings = [
      'The model should not pass the 8/10 threshold yet: the wall footprint and facade registration remain unverified, while the source-to-render comparisons still show meaningful architectural discrepancies.',
      'The orthophoto registration is useful for roof/eaves outline only; it does not support claims about wall centers, heights, structural interpretation, or exact roof shape.',
      'Highest-value next steps: derive a GIS-to-wall overlay using the correct building polygon and a defensible transform; improve roof silhouette against multiple attributed photos; remove or identify the opaque courtyard obstruction; compare facade openings to source elevations/photos.'
    ]
    return {'building':'Neil Armstrong Hall of Engineering','building_id':'neil_armstrong_hall','revision_reviewed':'R12.4','review_type':'independent_read_only_grade','asset':'modular/buildings/neil_armstrong_hall.blend','asset_sha256':actual_sha,'expected_asset_sha256':EXPECTED_SHA,'fresh_reopen_validation':reopened,'identity_root':root_identity,'portable_images':deps_clean,'mesh_material_coverage':material_coverage,'score':score,'max_score':10.0,'passed': score >= 8.0,'criteria':criteria,'evidence':[str(VALIDATION.relative_to(ROOT)),str(EVIDENCE.relative_to(ROOT)),'audit/neil_armstrong_hall_refine/comparison_plate_r12_1.png','audit/neil_armstrong_hall_refine/roof_trace_overlay_r12.png','audit/neil_armstrong_hall_refine/renders_r12_1/contact_r12_1.png','audit/neil_armstrong_hall_refine/comparison_notes_r12.md','audit/neil_armstrong_hall_refine/independent_review_r11.md','audit/complete_neil_armstrong/source_search_r11.json'],'findings':findings}


if __name__ == '__main__':
    result=evaluate()
    out=Path(__file__).with_name('independent_grade_r12_4.json')
    out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'score':result['score'],'passed':result['passed'],'sha256':result['asset_sha256'],'fresh_reopen_validation':result['fresh_reopen_validation']},indent=2))
