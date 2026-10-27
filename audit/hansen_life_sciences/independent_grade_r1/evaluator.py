import json, math, hashlib
from pathlib import Path
from shapely.geometry import Polygon
ROOT=Path('.')
OUT=ROOT/'audit/hansen_life_sciences/independent_grade_r1'
probe=json.loads((OUT/'fresh_open_probe.json').read_text(encoding='utf-8'))
evidence=json.loads((ROOT/'audit/hansen_life_sciences/evidence.json').read_text(encoding='utf-8'))
asset=ROOT/'modular/buildings/hansen_life_sciences.blend'
expected='fe0bc4834a9a14f3300587fff02d75171a7a54cc25ba6a12fd99f6c44526e552'
actual=hashlib.sha256(asset.read_bytes()).hexdigest()
source=Polygon(probe['source_ring_vertices_local_xy_m'])
model=Polygon(probe['model_top_perimeter_vertices_local_xy_m'])
if not source.is_valid or not model.is_valid: raise RuntimeError('Invalid structural/GIS polygon')
iou=source.intersection(model).area/source.union(model).area
haus=source.hausdorff_distance(model)
source_to_model=max(min(math.dist(x,y) for y in probe['model_top_perimeter_vertices_local_xy_m']) for x in probe['source_ring_vertices_local_xy_m'])
model_to_source=max(min(math.dist(x,y) for x in probe['source_ring_vertices_local_xy_m']) for y in probe['model_top_perimeter_vertices_local_xy_m'])
bounds_error=max(abs(source.bounds[i]-model.bounds[i]) for i in range(4))
criteria=[
 {'name':'Correct identity and source-backed footprint','score':2.0,'max_score':2.0,'evidence':[
  'Purdue Campus GIS BuildingShapesZip4 FID 237 attributes identify HANS / Arthur G. Hansen Life Sciences Research Building at 201 S University Street.',
  f'Independent fresh-open comparison of the evaluated basement slab upper perimeter against the raw FID 237 ring yields IoU {iou:.9f}, symmetric Hausdorff {haus*1000:.4f} mm, max directed vertex distances {source_to_model*1000:.4f}/{model_to_source*1000:.4f} mm, and maximum bounds error {bounds_error*1000:.4f} mm.'
 ],'limitations':['The official GIS feature is a building-shape record, not a published surveyed wall line; geometry likely shares the model source and is not an independent survey.']},
 {'name':'Position, orientation, and scale/dimensions','score':1.8,'max_score':2.0,'evidence':[
  'The model is stored in the expected local frame with AssetRoot at identity; its perimeter matches all 26 transformed GIS vertices and the transformed plan is 59.779 x 46.049 m.',
  'The manifest placement origin is [-288, -570] m and matches the source-register transform convention.'
 ],'limitations':['The independent grade reopened the individual library, not the campus master; it did not freshly inspect the master Placement_hansen_life_sciences marker. The GIS CRS is geographic and uses the documented local approximation rather than survey coordinates.']},
 {'name':'Evidence-backed height, floors, and roof form','score':1.0,'max_score':2.0,'evidence':[
  'Purdue Archives describes a four-story building; the asset has four above-grade floor plates and a basement, which is consistent with the historical narrative and the cited 2013 emergency-plan floor list.',
  'The model has a flat roof deck, penthouse/parapet, and rooftop exhaust stacks.'
 ],'limitations':['Purdue GIS reports six levels and vertical fields 60/67 without units/datum, conflicting with the four-story archive description and basement-plus-floors-1–4 emergency-plan list. The modeled roof deck (17.5 m), penthouse (20.572 m), and stack top (24.147 m) are unverified estimates; roof profile/mechanical elevations lack an as-built section.']},
 {'name':'Facade, entrances, and distinctive architecture','score':1.2,'max_score':2.0,'evidence':[
  'The saved exterior preview shows a coherent four-level research-building envelope with brick-colored wall planes, continuous horizontal glazing, pale floor bands, a stepped footprint, and a flat-roof penthouse.',
  'Purdue’s building record supports multidisciplinary laboratory use; the Purdue Events location page has a single 2022 user-posted building photo that can serve only as a visual cross-check.'
 ],'limitations':['No authoritative multi-elevation set or as-built facade drawings were located. Window-bay rhythm, brick/precast material boundaries, exact entrance/canopy forms, and rooftop equipment placement remain weakly supported or estimated; room interiors are intentionally unmodeled/unverified.']},
 {'name':'Modular export, portability, and complete evidence','score':2.0,'max_score':2.0,'evidence':[
  'A separate Blender 5.2.3 process opened the exact SHA and confirmed the expected scene, collection, identity-transform root, 816 collection objects, 809 mesh objects, assigned materials, no linked libraries, and no external image dependencies.',
  'The building folder includes the raw GIS response, evidence record, source/uncertainty notes, preview, and reproducible structural-outline comparison.'
 ],'limitations':[]}
]
score=round(sum(c['score'] for c in criteria),2)
result={
 'building_id':'hansen_life_sciences',
 'building_name':'Arthur G. Hansen Life Sciences Research Building',
 'asset':'modular/buildings/hansen_life_sciences.blend',
 'inspected_sha256':actual,'expected_sha256':expected,'sha_match':actual==expected,
 'independent_review':True,'fresh_open_blender_version':probe['blender_version'],
 'score':score,'max_score':10,'pass_threshold':8.0,'passed':score>=8.0 and actual==expected,
 'criteria':criteria,
 'evidence':[
  'audit/hansen_life_sciences/independent_grade_r1/fresh_open_probe.json',
  'audit/hansen_life_sciences/evidence.json',
  'audit/hansen_life_sciences/hansen_fid_237_gis.json',
  'audit/hansen_life_sciences/preview_oblique.png',
  'audit/hansen_life_sciences/independent_grade_r1/evaluator.py',
  'Purdue Campus GIS BuildingShapesZip4 FID 237: '+evidence['sources'][0]['url'],
  'Purdue Archives historic entity record: '+evidence['sources'][1]['url'],
  'Purdue Events HANS location/photo page: '+evidence['sources'][3]['url']
 ],
 'findings':[
  f'PASS at {score:.2f}/10. The plan geometry is extremely close to the cited GIS polygon, but this proves consistency with that map feature, not survey-grade wall placement.',
  'The four-story count has Purdue archival support; the GIS six-level/vertical-attribute fields conflict and do not document units. Roof and equipment elevations remain estimates.',
  'Exterior form and materials are plausible and cleanly modeled, but facade, entrance and rooftop details are not independently documented by measured elevations. No verified interior layout is included.',
  'Fresh-open review covered the library only; master placement-marker integration remains a coordinator-side check.'
 ],
 'geometry_comparison':{'source_area_m2':source.area,'model_area_m2':model.area,'intersection_over_union':iou,'symmetric_hausdorff_m':haus,'max_source_vertex_to_model_vertex_m':source_to_model,'max_model_vertex_to_source_vertex_m':model_to_source,'max_bounds_axis_error_m':bounds_error},
 'limitations':['Purdue GIS capture date/accuracy is unpublished.','The local transform is an approximation, not a surveyed CRS.','No as-built elevations, roof section, or accessible internal CAD floor plans were found.','1983 archive record versus 1984 university timeline completion year is unresolved.']
}
(OUT/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
report=f'''# Independent grade — Arthur G. Hansen Life Sciences Research Building\n\n**Result: {score:.2f}/10 — {'PASS' if result['passed'] else 'FAIL'}**\n\n**Frozen asset SHA-256:** `{actual}`  \n**Fresh-open version:** {probe['blender_version']}\n\n## Criteria\n\n| Criterion | Score | Evidence / limitations |\n| --- | ---: | --- |\n'''
for c in criteria:
    report+='| '+c['name']+' | '+f"{c['score']:.2f}/{c['max_score']:.0f}"+' | '+ ' '.join(c['evidence']+c['limitations']).replace('|','/')+' |\n'
report+='\n## Independent geometry measurements\n\n'
report+=f"- GIS/model area: {source.area:.6f} / {model.area:.6f} m².\n- Intersection over union: {iou:.9f}.\n- Symmetric Hausdorff distance: {haus*1000:.4f} mm.\n- Maximum axis bound difference: {bounds_error*1000:.4f} mm.\n- Fresh-open asset objects: {probe['object_count']} total, {probe['mesh_object_count']} meshes; {probe['material_count_assigned']} assigned materials; no linked libraries or external image dependencies.\n"
report+='\n## Findings and remaining uncertainty\n\n'
for item in result['findings']: report+='- '+item+'\n'
report+='\n## Sources\n\n'
for item in result['evidence'][5:]: report+='- '+item+'\n'
report+='\nThis review scores the frozen library only; Tobin must still validate the master placement marker during integration.\n'
(OUT/'grade_report.md').write_text(report,encoding='utf-8')
print(json.dumps({'score':score,'passed':result['passed'],'sha':actual,'iou':iou,'hausdorff_m':haus,'bounds_error_m':bounds_error},indent=2))
