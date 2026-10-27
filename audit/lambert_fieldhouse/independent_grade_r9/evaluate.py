import json
from pathlib import Path
out=Path(__file__).resolve().parent
probe=json.loads((out/'fresh_open_probe.json').read_text(encoding='utf-8'))
validation=json.loads((out.parent/'validation_round9.json').read_text(encoding='utf-8'))
evidence=json.loads((out.parent/'evidence_round9.json').read_text(encoding='utf-8'))
criteria=[
 {'criterion':'Correct identity and source-backed footprint','score':1.9,'max_score':2.0,'evidence':'Correct Lambert Fieldhouse/Gymnasium identity is supported by Purdue Athletics; the current exported GIS shell is explicitly tied to Purdue ArcGIS BuildingShapesZip4 feature 261, and validation says the 20-edge footprint is retained. The official facility source confirms the six-lane 200 m track. The footprint itself is a current GIS record, not a historic building survey; the archive dimensions do not georegister the two building volumes.'},
 {'criterion':'Position, orientation, and scale/dimensions','score':1.4,'max_score':2.0,'evidence':'The local GIS shell bounds are symmetric at about 99.31 x 93.84 m, and the modeled hall and gym dimensions convert consistently from the cited archival 303 x 172 ft and 210 x 110 ft dimensions. However, the available archive does not georegister either rectangular volume against the U-shaped GIS outline. Their relative allocation and exact placement remain an explicit hypothesis, so the model cannot claim a verified fit to the current building walls.'},
 {'criterion':'Evidence-backed height, floors, and roof form','score':1.5,'max_score':2.0,'evidence':'A one-story fieldhouse and separate four-story gym are supported by the cited Purdue historical record; the candidate shows a broad arched hall roof and flat gym roof. The archival source has no measured elevations or roof sections. R9 records 11.2 m fieldhouse wall height, 17.66 m crown, and roughly 13.43 m gym roof as estimates, correctly labeled illustrative.'},
 {'criterion':'Facade, entrances, and distinctive architecture','score':1.5,'max_score':2.0,'evidence':'The exterior render shows a coherent red-brown brick fieldhouse/gym composition, repeated openings, pale concrete/limestone bands and pilasters, and a glazed entry area. The packed brick texture and procedural relief improve material scale, and the detached GIS bands and unsupported tower were removed. Window cadence, exact entrance composition and facade details remain schematic; the available visual sources do not establish their dimensions.'},
 {'criterion':'Modular export, portability, and complete evidence','score':1.7,'max_score':2.0,'evidence':f"Blender {probe['blender_version']} freshly reopened the exact candidate SHA-256 {probe['sha256']}. Expected Asset_lambert_fieldhouse contains 914 objects including 909 meshes, every mesh has a material, the brick image is packed, and there are no linked libraries. Revision-specific source, validation, and render evidence are present. Deducted for three site context meshes (Stadium sidewalk, curb, Stadium Avenue roadway) remaining inside the exported building collection, plus master-placement review still being required before canonical promotion."}
]
score=round(sum(x['score'] for x in criteria),2)
result={
 'review_type':'independent fresh-open and evidence-based grade',
 'review_date':'2026-10-26',
 'building_id':evidence['building_id'],
 'name':evidence['name'],
 'candidate':evidence['candidate_asset'],
 'candidate_sha256':probe['sha256'],
 'blender_version':probe['blender_version'],
 'score':score,'max_score':10.0,'pass_threshold':8.0,'passed':score>=8.0,
 'criteria':criteria,
 'evidence':[
  {'type':'fresh Blender reopen','path':'audit/lambert_fieldhouse/independent_grade_r9/fresh_open_probe.json','summary':f"Expected collection reopened; {probe['collection_objects']} collection objects, {probe['mesh_objects']} meshes, zero mesh material gaps, packed brick image, zero linked libraries."},
  {'type':'round 9 geometry/evidence record','path':'audit/lambert_fieldhouse/evidence_round9.json','summary':'Current GIS footprint retained; archival volume dimensions and floor counts are labeled; unresolved hall/gym registration and elevation limits are explicit.'},
  {'type':'candidate validation','path':'audit/lambert_fieldhouse/validation_round9.json','summary':'Fresh reopen PASS, expected export collection present, six-lane path length 199.989 m, no hurdle meshes without materials; reports revised bounds and material nodes.'},
  {'type':'render review','path':'audit/lambert_fieldhouse/exterior_round9.png','summary':'Shows the hall/gym massing, entry, red brick facade, window rhythm and arched fieldhouse roof; overall design remains simplified and exact wall registration is not visually verified.'},
  {'type':'render review','path':'audit/lambert_fieldhouse/interior_round9_cutaway.png','summary':'Shows the oval track and seating in a cutaway view with roof and shell hidden for inspection.'},
  {'type':'render review','path':'audit/lambert_fieldhouse/interior_event_round9.png','summary':'Shows seating, event hurdles and high jump area; event equipment/layout is illustrative.'},
  {'type':'primary source','url':'https://purduesports.com/facilities/lambert-fieldhouse','summary':'Purdue Athletics confirms the facility identity/location, current indoor track use, and six-lane 200 m Rekortan track.'},
  {'type':'primary source','url':'https://collections.lib.purdue.edu/campus/buildings/92','summary':'Purdue Archives historical database cited for hall/gym plan dimensions and story counts; it does not provide the spatial registration or measured elevations needed to verify the current arrangement.'}
 ],
 'findings':[
  'PASS at the project 8/10 threshold (8.0/10). This is a narrow pass; the design is detailed and the export is portable, but evidence limits on volume placement remain material.',
  'Before canonical master integration, isolate the three Stadium sidewalk/curb/road meshes from Asset_lambert_fieldhouse or establish that the master does not already contain duplicates.',
  'The archive dimensions establish the historic volumes but do not register them to the current GIS footprint. Treat hall/gym placement as estimated and inspect the candidate against the master, orthophoto, and current street-level imagery before accepting its campus fit.',
  'Heights, floor-to-floor intervals, roof crown, gym floorplan/interior, facade bay cadence, and current entrance details remain estimates or visually inferred.'
 ],
 'master_integration_status':'not reviewed in this asset-only grade; candidate remains at audit/lambert_fieldhouse/lambert_fieldhouse_r9_candidate.blend and is not the canonical asset.'
}
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'score':score,'passed':result['passed'],'criteria':criteria},indent=2))
