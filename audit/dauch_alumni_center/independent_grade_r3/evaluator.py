"""Independent rubric evaluator for frozen Dauch Alumni Center R3."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
F=json.loads((HERE/'fresh_open_probe.json').read_text(encoding='utf-8'))
EXPECTED='de1e3735f6b9f206f53cc1affb13c208ae62e96f1322eea6aeed378af9d37d14'
assert F['fresh_open'] and F['blender_version'].startswith('5.2.3')
assert F['sha_match'] and F['asset_sha256']==EXPECTED
assert F['collection']=='Asset_dauch_alumni_center' and F['collection_is_scene_linked']
assert F['source_ring_vertices']==109 and F['shell_unique_xy_vertices']==109
assert F['footprint_max_nearest_error_m'] < 2e-6
assert F['shell_topology']['side_normals']=={'outward':109,'inward':0,'ambiguous':0}
assert F['shell_topology']['signed_volume_m3'] > 0
assert not F['external_image_dependencies'] and F['zero_area_mesh_faces']==0
criteria=[
 {'name':'Correct identity and source-backed footprint','score':2.0,'max_score':2.0,'evidence':['Purdue BuildingShapesZip4 feature FID 71 names Dick & Sandy Dauch Alumni Center at 403 W Wood Street.','Independent source-ring comparison found 109 unique GIS perimeter points and 109 shell XY positions; maximum nearest-point error is 0.00000146 m.'],'finding':'Building identity and plan geometry are strongly and directly supported by the official Purdue GIS footprint.'},
 {'name':'Position, orientation, and scale/dimensions','score':1.9,'max_score':2.0,'evidence':['The independently calculated GIS polygon centroid is [241.198987, -618.185206] m; the asset placement origin differs by less than 1e-11 m.','The exported geometry remains in the expected local coordinate frame. The structural shell reproduces the source ring without rescaling; full asset bounds include a documented southward sign/landscape extension.'],'finding':'Horizontal placement, orientation, and footprint scale are well supported. Decorative bounds extend beyond the GIS wall footprint as expected; height and exact architectural dimensions are separately uncertain.'},
 {'name':'Evidence-backed height, floors, and roof form','score':1.25,'max_score':2.0,'evidence':['The saved Purdue GIS feature reports four levels and its level datum fields; Purdue’s historic building database describes the facility as three-story. Evidence explicitly preserves rather than guesses away this conflict.','The roof membrane is a separate 1,075-vertex surface with a 0.90 m crown above the structural cap. The roof profile/material now read as a subtle curved gray membrane in the R3 views, consistent with the cited exterior photo, but no measured section or roof schedule was found.','The 14.4 m shell top, 15.305 m roof crest, and overall height are estimates. The above-grade floor count remains provisional.'],'finding':'R3 fixes the incorrect winding and flat striped roof presentation, but the roof curve and vertical dimensions are not measured, and the story-count conflict remains unresolved.'},
 {'name':'Facade, entrances, and distinctive architecture','score':1.5,'max_score':2.0,'evidence':['The overview shows brick exterior, horizontal light courses, a projecting glazed entrance, approach flagpoles, and a readable freestanding identity sign; these features are supported by Purdue for Life and Home of Purdue building-specific photos.','The curved frontage and roof edge are present, but window subdivisions, facade bay rhythm, precise entry proportions, side elevations, and sign/landscape placement remain approximate. The interiors are schematic because the Archives floorplan was not retrieved.'],'finding':'Recognizable brick-and-glass character and entrance/site identity are represented; facade details and interiors remain interpretive.'},
 {'name':'Modular export, portability, and complete evidence','score':1.8,'max_score':2.0,'evidence':['Separate Blender 5.2.3 process reopened the requested exact SHA and found the expected Scene and scene-linked Asset_dauch_alumni_center collection, with 663 objects including 659 meshes.','The 29 used materials are node-based; no external image dependencies or zero-area mesh faces were found. The shell is closed and consistently wound with positive signed volume 25,313.66 m³.','Building evidence records source URLs, GIS feature ID, retrieval dates, coordinate method, changes, bounds, and unresolved limits. The absent archival floorplan and non-surveyed vertical dimensions remain documented.'],'finding':'The library is portable and well documented. Master linkage and shared manifest refresh are outside this isolated asset grade; the bounds report is ready for coordinator integration.'}
]
score=round(sum(c['score'] for c in criteria),2)
result={'building':'Dick & Sandy Dauch Alumni Center','building_id':'dauch_alumni_center','review_revision':3,'asset':'modular/buildings/dauch_alumni_center.blend','asset_sha256':F['asset_sha256'],'expected_sha256':EXPECTED,'exact_sha_match':True,'review_date':'2026-10-27','reviewer':'independent grader','blender_version':F['blender_version'],'fresh_open':F['fresh_open'],'score':score,'max_score':10.0,'threshold':8.0,'accepted':score>=8.0,'criteria':criteria,'evidence':{'footprint_max_error_m':F['footprint_max_nearest_error_m'],'gis_polygon_centroid_world_m':F['gis_polygon_centroid_world_m'],'placement_origin_xy_m':F['placement_origin_xy_m'],'origin_error_m':F['origin_error_m'],'shell_topology':F['shell_topology'],'asset_bounds_local_m':F['all_mesh_bounds_local_m'],'roof_surfaces':F['roof_surfaces'],'used_material_count':F['used_material_count'],'external_image_dependencies':F['external_image_dependencies'],'zero_area_mesh_faces':F['zero_area_mesh_faces'],'source_records':['Purdue BuildingShapesZip4, feature 71 (audit/dauch_alumni_center/dauch_alumni_center_gis_feature_71.json)','Purdue for Life Foundation, Dauch Alumni Center photo (URL and limits in audit/dauch_alumni_center/dauch_alumni_center_evidence.json)','Home of Purdue building-specific photo (URL and limits in audit/dauch_alumni_center/dauch_alumni_center_evidence.json)','Purdue Campus Facilities and Buildings Historic Database: Dick & Sandy Dauch Alumni Center','Purdue Archives UA 137 Dauch Alumni Center records/finding aid']},'findings':['The 109 GIS footprint vertices align within 0.00000146 m and the asset origin matches the computed footprint centroid within 1e-11 m.','All 109 GIS shell side faces point outward; the closed shell has positive signed volume and correctly oriented top and bottom caps.','The roof is now modeled with an estimated curved crown and neutral-gray membrane. Its exact section, elevation, and upper facade levels lack measured documentation.','Purdue’s historic record says three-story while GIS reports four levels; this conflict remains explicitly unresolved. The rendered building remains recognizably brick-and-glass with a glazed entrance, flags, and sign, but facade rhythm and interior remain schematic.']}
(HERE/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
rows='\n'.join(f"| {c['name']} | {c['score']:.2f}/{c['max_score']:.2f} | {c['finding']} |" for c in criteria)
report=f'''# Independent grade — Dauch Alumni Center R3

**Score: {score:.2f}/10 — {'PASS' if result['accepted'] else 'FAIL'} (minimum 8.0).** Exact inspected asset SHA-256: `{F['asset_sha256']}`. The file was reopened in a separate Blender 5.2.3 LTS process and its shell was independently compared with the Purdue GIS feature.

## Rubric

| Criterion | Score | Evidence and finding |
|---|---:|---|
{rows}

## Fresh-open findings

- The expected scene and collection reopen with the requested SHA. The collection contains 663 objects (659 meshes).
- The official FID 71 outer ring has 109 unique points; maximum nearest-point error to the structural shell is 0.00000146 m. The local placement origin matches the transformed polygon centroid within 1e-11 m.
- The shell is watertight, has no zero-area faces, and has positive signed volume 25,313.66 m³. All 109 side faces point outward; top and bottom caps point up and down.
- The roof membrane has 1,075 vertices and rises approximately 0.90 m above the structural cap. It is a curved, neutral-gray surface, though the exact profile/elevation remains estimated.
- Used materials are node-based and no external image files are referenced.

## Remaining uncertainty

The GIS reports four levels while Purdue’s historic database says three stories; no measured section resolves this. Roof and total height, roof profile, facade bay dimensions, most unphotographed elevations, and interior room locations remain estimates or schematic. Sign and planting positions are photo-based approximations.

Probe data: `fresh_open_probe.json`; Blender log: `blender.log`; evaluator: `evaluator.py`.
'''
(HERE/'grade_report.md').write_text(report,encoding='utf-8')
print(json.dumps({'score':score,'accepted':result['accepted'],'sha256':F['asset_sha256']},indent=2))
