from pathlib import Path
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BUILDING='bindley_bioscience_center'
probe=json.loads((HERE/'blender_probe.json').read_text(encoding='utf-8'))
evidence=json.loads((ROOT/'audit'/BUILDING/'evidence.json').read_text(encoding='utf-8'))
validation=json.loads((ROOT/'audit'/BUILDING/'validation.json').read_text(encoding='utf-8'))
source=json.loads((ROOT/'audit'/BUILDING/'sources/gis_feature_605.json').read_text(encoding='utf-8'))
assert probe['collection_reopened'] and probe['export_reopened']
assert probe['gis_feature_id']==605 and probe['gis_ring_vertex_count']==191
assert Path(ROOT/'modular/buildings/build_bindley_bioscience_center.py').exists()
assert all((ROOT/p).exists() for p in probe['preview_files'])

criteria=[
 {
  'name':'Correct identity and source-backed footprint','score':2.0,'max_score':2.0,
  'evidence':[
   'Official Purdue BuildingShapes feature 605 matches BIND, full name Bindley Bioscience Center, and address 1203 Mitch Daniels Blvd.',
   f'The checked-in GIS snapshot contains {probe["gis_ring_vertex_count"]} unique exterior vertices; the reopened BIND_GIS_primary_shell has 191 base and 191 top vertices.',
   f'Using the documented local geographic conversion, symmetric GIS-to-shell Hausdorff residual is {probe["footprint_hausdorff_m"]["max_symmetric_m"]:.8f} m and the maximum XY bounds difference is {probe["max_xy_bounds_delta_m"]:.8f} m.'
  ],
  'findings':['Identity and full primary footprint are verified; no field survey was conducted.']
 },
 {
  'name':'Position, orientation, and scale/dimensions','score':2.0,'max_score':2.0,
  'evidence':[
   f'The area centroid derived from the official GIS ring equals the manifest placement origin; residual is {max(abs(x) for x in probe["placement_origin_residual_m"]):.8f} m.',
   f'Applying that origin once places the reopened shell within {probe["placed_world_footprint_hausdorff_m"]["max_symmetric_m"]:.8f} m of the projected source ring.',
   'The complete ordered geometry is preserved without rescaling; source and shell XY bounds agree within approximately 0.000002 m.'
  ],
  'findings':['Coordinates are based on Purdue’s documented local approximation, not a field-survey coordinate system.']
 },
 {
  'name':'Evidence-backed height, floors, and roof form','score':0.8,'max_score':2.0,
  'evidence':[
   'Official GIS fields NUM_LEVELS=3 and CountOfFLO=3 support a three-level model; the official Bindley photograph visibly supports a multistory glazed frontage.',
   f'The GIS shell is {probe["shell_bounds_local_m"][2][1]:.2f} m high and the complete modeled collection reaches {probe["overall_asset_bounds_local_m"][2][1]:.2f} m, including roof plant screens. The evidence record states 13.3 m eave and 14.55 m top estimates, so the highest modeled elements exceed that stated top estimate by 1.25 m.',
   'No as-built elevation or section was included. The GIS Extrution=19 and R=48 fields have no verified vertical semantics; the photographed roof is not sufficient to validate the modeled low-slope roof or roof plant.'
  ],
  'findings':['Modeled height and roof silhouette remain estimates/unverified; the GIS floor count supports only the number of levels. The measured asset roof-plant top (15.8 m) conflicts with the evidence record’s 14.55 m overall-top estimate.']
 },
 {
  'name':'Facade, entrances, and distinctive architecture','score':1.2,'max_score':2.0,
  'evidence':[
   'Purdue’s building-specific exterior photo and Flad project photos support light silver/white cladding, broad glazed volumes, a prominent lobby frontage, entry canopy, and dark name wall.',
   'The overview and entry_detail renders show light panels, a broad central glazed bay, repeated research windows, and a canopy.',
   'The renders do not represent the photo’s large dark name wall/sign band or the documented relationship between that wall and the glazed entrance; the model instead places a small light label over glass. Exact bay spacing and unphotographed elevations remain schematic.'
  ],
  'findings':['Photo-backed cladding and glazing cues are present, but the most distinctive signage wall and entrance composition are missing; the roof-height evidence also conflicts with the modeled rooftop screens.']
 },
 {
  'name':'Modular export, portability, and complete evidence','score':1.5,'max_score':2.0,
  'evidence':[
   f'The expected collection {probe["expected_collection"]} reopened from the saved asset with {probe["collection_object_count"]} objects; a collection-only library export reopened with the same count and no cameras or lights.',
   f'The reopened asset has {len(probe["external_unpacked_images"])} unpacked external images and {len(probe["linked_library_paths"])} linked libraries.',
   'Dedicated builder script, raw GIS snapshot, Purdue facility/facilities and Office of Research pages, building-specific photo, Flad architect page/photos/lookbook, evidence record, validation report, and three rendered views are present.',
   f'The shared manifest currently lists {probe["manifest_object_count"]} objects while the reopened export has {probe["collection_object_count"]}; its object-name set does not match. The preview rig remains in the saved source scene but is excluded from the exported asset collection.'
  ],
  'findings':['Coordinator should refresh manifest objects/object_count to the actual collection before treating the modular metadata as integrated.']
 }
]
score=round(sum(c['score'] for c in criteria),2)
findings=[f for c in criteria for f in c['findings']]
result={
 'building_id':BUILDING,
 'score':score,
 'max_score':10,
 'pass_threshold':8,
 'passed':score>=8,
 'criteria':criteria,
 'evidence':{
  'asset':probe['asset_file'],
  'asset_sha256':probe['asset_sha256'],
  'evaluator_probe':'audit/bindley_bioscience_center_independent_grade/blender_probe.json',
  'source_record':'audit/bindley_bioscience_center/evidence.json',
  'gis_snapshot':'audit/bindley_bioscience_center/sources/gis_feature_605.json',
  'validation_report':'audit/bindley_bioscience_center/validation.json',
  'rendered_views':probe['preview_files'],
  'collection_export_probe':probe['collection_export_probe']
 },
 'findings':findings
}
(HERE/'result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
