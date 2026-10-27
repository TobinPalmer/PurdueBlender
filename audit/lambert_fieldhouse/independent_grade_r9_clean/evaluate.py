import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
probe=json.loads((OUT/'fresh_open_probe.json').read_text(encoding='utf-8'))
validation=json.loads((ROOT/'audit/lambert_fieldhouse/validation_round9.json').read_text(encoding='utf-8'))
evidence=json.loads((ROOT/'audit/lambert_fieldhouse/evidence_round9.json').read_text(encoding='utf-8'))
source=json.loads((ROOT/'audit/batchC_lambert_official_footprint.json').read_text(encoding='utf-8'))
feature=source['features'][0]
attrs=feature['attributes']
checks={
 'source_feature_id':attrs.get('FID'),
 'source_abbreviation':attrs.get('BLDG_ABBR'),
 'source_name':attrs.get('BUILDING_N'),
 'gis_footprint_object_found':probe['gis_footprint_object_found'],
 'gis_ring_vertex_count':probe['source_footprint']['ring_vertices_excluding_closure'],
 'gis_asset_boundary_vertex_count':probe['footprint_comparison']['unique_asset_xy_vertices'],
 'gis_to_asset_max_vertex_error_m':max(probe['footprint_comparison']['source_to_mesh_max_nearest_vertex_error_m'],probe['footprint_comparison']['mesh_to_source_max_nearest_vertex_error_m']),
 'gis_bbox_max_edge_error_m':probe['footprint_comparison']['bounds_max_abs_error_m'],
 'documented_local_anchor_xy_m':probe['source_footprint']['converted_bbox_anchor_xy_m'],
 'candidate_sha_matches_evidence':probe['sha256']==evidence['candidate_sha256'],
 'fresh_open_pass':probe['status']=='PASS',
 'materialless_meshes':len(probe['materialless_meshes']),
 'site_context_meshes_remaining':len(probe['removed_context_objects_still_in_export']),
 'track_centerline_perimeter_m':probe['track_lane_one_centerline_perimeter_m'],
 'track_delta_from_200m':abs(probe['track_lane_one_centerline_perimeter_m']-200.0),
 'hurdle_meshes':probe['hurdle_mesh_count'],
 'unpacked_image_count':sum(not im['packed'] for im in probe['external_images']),
 'linked_library_count':len(probe['linked_libraries'])
}
criteria=[
 {'criterion':'Correct identity and source-backed footprint','score':1.9,'max_score':2.0,'evidence':f"The saved Purdue ArcGIS source feature is FID {attrs.get('FID')} ({attrs.get('BLDG_ABBR')}, {attrs.get('BUILDING_N')}); the asset contains the named current GIS ground-footprint mesh. An independent projection of all 20 GIS vertices into the documented campus-local frame matches the asset footprint within 0.000002 m in both directions, with 0.0000014 m maximum bounding-edge error. The current Purdue Athletics page identifies Lambert Fieldhouse as its track-and-field home and states it contains a six-lane, 200-meter Rekortan track. The GIS polygon does not identify the archival hall/gym split or verify the exterior wall envelope."},
 {'criterion':'Position, orientation, and scale/dimensions','score':1.4,'max_score':2.0,'evidence':'The exported footprint matches the official GIS polygon within 0.000002 m; its bbox midpoint agrees with the documented local-coordinate anchor, and the lane-one track centerline independently measures 199.989 m. Purdue Archives evidence supports 303 x 172 ft for the fieldhouse and 210 x 110 ft for the gym; candidate dimensions are converted consistently. The archive does not georegister the historical plan rectangles against the present U-shaped GIS footprint, so fit and relative placement of the actual hall/gym volumes remain unverified.'},
 {'criterion':'Evidence-backed height, floors, and roof form','score':1.5,'max_score':2.0,'evidence':'The cited Purdue Archives record supports a one-story fieldhouse and a separate four-story gym; the candidate has a broad arched fieldhouse roof and a lower flat gym roof. R9 explicitly labels the wall and roof heights as illustrative estimates. No measured elevations, roof section, truss spacing, floor-to-floor heights, or current roof profile are supplied, so the silhouette is plausible but not metrically confirmed.'},
 {'criterion':'Facade, entrances, and distinctive architecture','score':1.5,'max_score':2.0,'evidence':'I inspected the regenerated exterior and interior/event renders. The exterior depicts a broad arched hall roof, brick walls with repeated openings, pale vertical and horizontal detailing, and a glazed entrance; the interior shows a red six-lane track, seating, hurdles and high-jump equipment. Materials have surface variation and a packed brick image. Exact window rhythm, facade dimensions, entrance composition and current tower condition are not established by the sources; the model remains simplified and event equipment/interior layout is illustrative.'},
 {'criterion':'Modular export, portability, and complete evidence','score':1.9,'max_score':2.0,'evidence':f"A fresh Blender {probe['blender_version']} process opened the exact candidate SHA {probe['sha256']}. Asset_lambert_fieldhouse contains {probe['collection_objects']} objects ({probe['mesh_objects']} meshes); every mesh has a material, the brick image is packed, there are no linked libraries, and the previously identified sidewalk/curb/road context meshes are absent. The candidate includes revision-specific evidence, validation, renders, and explicit uncertainty. The remaining 0.1 deduction reflects that this is still a candidate: placement at the master marker and fit against nearby campus context have not been independently checked in the full master."}
]
score=round(sum(c['score'] for c in criteria),2)
result={
 'review_type':'independent fresh-open, source-based and visual grade',
 'review_date':'2026-10-26',
 'building_id':evidence['building_id'],
 'name':evidence['name'],
 'candidate':evidence['candidate_asset'],
 'candidate_sha256':probe['sha256'],
 'blender_version':probe['blender_version'],
 'score':score,'max_score':10.0,'pass_threshold':8.0,'passed':score>=8.0,
 'criteria':criteria,
 'evidence':[
  {'type':'fresh Blender reopen','path':'audit/lambert_fieldhouse/independent_grade_r9_clean/fresh_open_probe.json','summary':f"PASS; exact candidate SHA reopened with {probe['collection_objects']} exported objects, {probe['mesh_objects']} meshes, no unassigned mesh materials, no linked libraries, one packed image, no site-context meshes, six-lane track centerline {probe['track_lane_one_centerline_perimeter_m']:.6f} m."},
  {'type':'source GIS snapshot','path':'audit/batchC_lambert_official_footprint.json','summary':f"Purdue University ArcGIS BuildingShapesZip4 feature FID {attrs.get('FID')} / {attrs.get('BLDG_ABBR')}, identified as {attrs.get('BUILDING_N')}; polygon is current footprint evidence but does not locate the historical volumes within it."},
  {'type':'revision-specific evidence and validation','path':'audit/lambert_fieldhouse/evidence_round9.json','summary':'Records source URLs/providers, conversions, measured track geometry, changes, and unresolved hall/gym registration and elevation limits; validation_round9.json records fresh reopen and material checks.'},
  {'type':'exterior and interior visual review','paths':['audit/lambert_fieldhouse/exterior_round9.png','audit/lambert_fieldhouse/interior_round9_cutaway.png','audit/lambert_fieldhouse/interior_event_round9.png'],'summary':'Exterior shows the hall/gym form and facade treatment; interior views show the track, seating and event details. Appearance supports broad typology only, not exact measured placement or architecture.'},
  {'type':'official facility source','url':'https://purduesports.com/facilities/lambert-fieldhouse','summary':'Purdue Athletics identifies the facility at Northwestern and Stadium Avenues, says it is the home of Purdue track and field, and describes a six-lane 200-meter Rekortan track.'},
  {'type':'historical dimensional source','url':'https://archives.lib.purdue.edu/agents/corporate_entities/559','summary':'Purdue Archives identifies the original 1937 building as a one-story fieldhouse plus 110 by 210 foot four-story gym, with a 172 by 303 foot fieldhouse. These historical facts do not georeference present volumes or provide measured elevations.'},
  {'type':'original historic database record','url':'https://collections.lib.purdue.edu/campus/buildings/92','summary':'The cited Purdue Campus Facilities and Buildings Historic Database record; the current page is minimally rendered, and the Archives description supplies the historical dimensional text.'},
  {'type':'interior photo reference','url':'https://pinolaphoto.com/2019/01/14/gene-edmonds-invitational/','summary':'2019 photographer coverage describes a new track and provides event/interior imagery as non-metric visual context.'},
  {'type':'historic postcard','url':'https://commons.wikimedia.org/wiki/File:Purdue_fieldhouse_and_gymnasium,_Purdue_University,_West_Lafayette,_Indiana_(77515).jpg','summary':'Boston Public Library postcard is dated circa 1930–1945; it supports historic material/massing context only and cannot establish survival or current dimensions.'}
 ],
 'independent_checks':checks,
 'findings':[
  'PASS at the project threshold (8.2/10). The cleaned asset is portable, freshly reopened, uses the expected export collection, has complete mesh materials, and no longer exports road/sidewalk/curb context.',
  'The current GIS footprint, building identity, six-lane track and approximate archival floor-plan dimensions have documentary support. The historic rectangular volumes are not tied to the current U-shaped footprint by any source; their exact fit and relative placement remain an estimate.',
  'All vertical dimensions, roof curvature and several facade details remain illustrative or visually inferred. The interior event equipment and seating layout are representative, not a verified floorplan.',
  'Before coordinator promotion, verify the manifest marker location and inspect the candidate together with current orthophoto/master context. The asset-only grade does not validate neighboring-building collisions or registration of the hall/gym volumes.'
 ],
 'master_integration_status':'not reviewed; candidate remains at audit/lambert_fieldhouse/lambert_fieldhouse_r9_candidate.blend and is not canonical.'
}
(OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'score':score,'passed':result['passed'],'criteria':criteria,'checks':checks},indent=2))
