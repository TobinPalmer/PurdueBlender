from pathlib import Path
import hashlib, json, math
root=Path.cwd()
out=root/'audit/farmhouse_fraternity_purdue_chapter_independent_grade'
asset=root/'modular/buildings/massing_farmhouse_fraternity_purdue_chapter_0b8908b.blend'
expected='FA28A3E30FA5BB437026309CF1915EB5A30F928814A2BB9CEE3B9AADA8E83C04'
sha=hashlib.sha256(asset.read_bytes()).hexdigest().upper()
probe=json.loads((out/'blender_probe.json').read_text())
evidence=json.loads((root/'audit/farmhouse_fraternity_purdue_chapter/evidence.json').read_text())
assert sha==expected, f'Candidate SHA changed: {sha}'
assert probe['scene']=='Building_massing_farmhouse_fraternity_purdue_chapter_0b8908b'
assert probe['mesh_objects']==1 and len(probe['libraries'])==0
criteria=[
 {'name':'Correct identity and source-backed footprint','score':1.5,'max_score':2,
  'evidence':['OSM way 301923755 is explicitly named FarmHouse Fraternity, Purdue Chapter and tagged with 1028 State Street; the local source image shows the FarmHouse name sign and brick building.','The candidate building mesh bounds align with the OSM polygon bounds at approximately 27.67 x 38.99 m; the dedicated build script uses that exact outline.','Purdue/Tippecanoe GIS FID 778 is a conflicting authoritative geometry: approximately 29.90 x 21.85 m with 636.39 m² area vs OSM 740.24 m² and only 0.536 axis-aligned bounding-box IoU. The candidate record acknowledges this mismatch.'],
  'findings':['The conflict cannot be dated or resolved from available evidence: FID 778 exposes no source date and neither source supplies a survey. Calling the GIS polygon historical/partial is not established. Identity is strong, footprint source choice is defensible but uncertain.']},
 {'name':'Position, orientation, and scale/dimensions','score':1.8,'max_score':2,
  'evidence':['The asset is in campus-coordinate XY (not local-origin coordinates), matching the simple-massing compatibility rule.','Its base footprint is built directly from the OSM way’s campus-local transform and overall mesh bounds include the expected entry/roof projections.','Source conflict leaves exact surveyed dimensions unverified; no independent geodetic control or measured elevation was found.'],
  'findings':['Plan placement is supported by the OSM named geometry and aligns with the project’s original massing location, but this is not an independent survey check.']},
 {'name':'Evidence-backed height, floors, and roof form','score':0.8,'max_score':2,
  'evidence':['KJG project information supports four stories over a basement; the asset correctly labels overall height as estimated, not measured.','The saved render shows five repeated window rows above the basement/plinth, while the documented program says four stories above basement; build script defines five window bands and five floor-plate levels.','The main roof spans nearly the entire footprint at about 3.1 m rise over half-span about 12.5 m, roughly 14 degrees, and is a single simple gable. Source aerial/project photos show steep, intersecting roof wings and clear gables.'],
  'findings':['The floor/window stack appears one story too tall relative to the four-story source description. Main roof silhouette and pitch materially disagree with source photos; roof intersections/wings are omitted. Absolute eave/ridge heights remain unverified estimates.']},
 {'name':'Facade, entrances, and distinctive architecture','score':0.8,'max_score':2,
  'evidence':['Brick, limestone bands/quoins, divided sash, white eaves, and an entry portico are recognizable elements visible in the saved source photographs.','Fresh-open render has a repeated brick facade and window grid with material differentiation.','Reference entrance photos show a large white columned porch/portico extending along the facade and around the corner, along with a prominent FarmHouse name sign; the candidate has only a small corner canopy/entry and no sign.','Source photos show materially steeper, articulated roof edges and detailed gable treatment, while the model’s top reads nearly flat from the saved review camera.'],
  'findings':['Main entry scale and porch footprint are underrepresented; signature FarmHouse sign absent. Window rhythm is generic and appears five rows. Corner quoins are isolated small blocks, unlike the substantial repeated limestone blocks in photos.']},
 {'name':'Modular export, portability, and complete evidence','score':1.8,'max_score':2,
  'evidence':['Fresh-open in Blender 5.2 succeeds. Scene is Building_massing_farmhouse_fraternity_purdue_chapter_0b8908b; expected Asset_ collection exists.','The asset is compacted into one mesh object with 8,469 vertices and 4,009 polygons; no linked libraries, external images, or missing texture dependencies. Ten procedural material definitions are present.','Building evidence records source providers, URLs, feature IDs, retrieval date, CRS/method, source uncertainty, geometry, and edits.'],
  'findings':['All surface materials are procedural with no image textures; this is portable but provides no mapped photographic facade detail. The interior is only schematic and is not visible in the exterior-only saved review.']}
]
score=round(sum(c['score'] for c in criteria),1)
result={
 'candidate_path':'modular/buildings/massing_farmhouse_fraternity_purdue_chapter_0b8908b.blend',
 'candidate_sha256':sha,'sha256_verified':True,'fresh_open_verified':True,
 'evaluator':'Independent evaluator; direct Blender reopen/probe plus source snapshot and image inspection',
 'score':score,'max_score':10,'pass_threshold':8,'passes':score>=8,'criteria':criteria,
 'source_conflict':{
  'OSM_way_301923755':{'bounds_xy_m':evidence['comparison']['osm_bounds_xy_m'],'area_m2':evidence['geometry']['area_m2_from_osm'],'aabb_iou_vs_gis':evidence['comparison']['osm_aabb_iou_vs_tippecanoe']},
  'Purdue_Tippecanoe_FID_778':{'bounds_xy_m':evidence['comparison']['tippecanoe_fid_778_bounds_xy_m'],'area_m2':evidence['comparison']['tippecanoe_polygon_area_m2'],'aabb_iou_vs_osm':evidence['comparison']['osm_aabb_iou_vs_tippecanoe'],'resolution':'Unresolved: source date is absent from FID 778 record; available photos corroborate a substantial complex but cannot adjudicate its surveyed outline. Do not label FID 778 historical/partial as a fact.'}
 },
 'overall_findings':[
  'Strong building identity and evidence-supported placement, but the building fails the 8/10 threshold due to the floor-count/window-row mismatch, roof silhouette, and missing principal porch/signature entrance details.',
  'The OSM outline is a reasonable current-model choice because it is named and matches the original campus massing extents, but the source conflict remains open.'
 ]
}
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'candidate_sha256':sha,'score':score,'passes':result['passes'],'result':str(out/'result.json')},indent=2))
