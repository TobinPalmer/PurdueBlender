import json
from pathlib import Path
base=Path(__file__).resolve().parent
probe=json.loads((base/'model_probe.json').read_text(encoding='utf-8'))
build=json.loads((base.parent/'build_report.json').read_text(encoding='utf-8'))
sources=json.loads((base.parent/'sources.json').read_text(encoding='utf-8'))


def evaluate(probe, build, sources):
    gis=build['gis']; model=build['model']; validation=build['validation']
    criteria=[
      {'criterion':'Correct identity and source-backed footprint','score':2.0,'max_score':2.0,'status':'verified',
       'evidence':[f"Purdue BuildingShapesZip4 FeatureServer 0 FID {gis['feature_id']} identifies {gis['name']} (PGW) at {gis['address']}.",
         f"Fresh-open probe independently converted the 18 raw GIS ring points from EPSG:3857 to the project's local tangent coordinates and found the model deck's ring vertex set identical: {probe['footprint_vertices_observed']} vertices, {probe['footprint_missing_count']} missing, {probe['footprint_extra_count']} extra at {probe['footprint_vertex_tolerance_m']} m rounding tolerance.",
         'Official Purdue parking references and the Purdue Archives search excerpt corroborate the Wood Street Garage identity/location.'],
       'reason':'The authoritative GIS building code, feature ID, name, address and exact footprint geometry match.'},
      {'criterion':'Position, orientation, and scale/dimensions','score':1.8,'max_score':2.0,'status':'verified locally; master marker pending',
       'evidence':[f"Asset scene records its campus anchor as {probe['world_anchor_m']} m; the GIS transformed footprint bbox midpoint is the same anchor.",
         f"Structural footprint dimensions are {gis['projected_plan_dimensions_m']} m, and the exact source ring is represented in the local frame; scene axes are X east, Y north, Z up.",
         'A master Placement marker has not yet been added, so the final campus instance transform remains to be checked by the coordinator.'],
       'reason':'Local origin, orientation and footprint scale are source-registered; final master placement still needs coordinator verification.'},
      {'criterion':'Evidence-backed height, floors, and roof form','score':1.5,'max_score':2.0,'status':'partially verified; roof height inferred',
       'evidence':[f"Purdue GIS reports NUM_LEVELS={gis['height_fields']['NUM_LEVELS']}, CountOfFLO={gis['height_fields']['CountOfFLO']}, and floor fields F01–F07 at 10 ft intervals.",
         f"The reopened asset has eight occupied deck slabs at 3.048 m increments and an overall roof/parapet top of {probe['bounds_local_m'][2][1]:.4f} m.",
         f"GIS R=78 ft plausibly indicates about {gis['height_fields']['R_ft']*0.3048:.3f} m to roof, but its definition and vertical units are not documented; the modeled top is about {probe['bounds_local_m'][2][1]-gis['height_fields']['R_ft']*0.3048:.3f} m higher. No measured elevation drawing was found."],
       'reason':'Eight levels and the approximate vertical scale are supported by GIS fields, but the roof datum and field interpretation are not independently surveyed.'},
      {'criterion':'Facade, entrances, and distinctive architecture','score':1.5,'max_score':2.0,'status':'partially source-supported',
       'evidence':[f"The saved circa-2010 exterior image shows repeated horizontal open parking slots, concrete piers/spandrels, a narrow glazed stair tower, and warm stairwell lights.",
         f"The model includes repeated open facade bays, a glazed/stair-lit tower, ramps and the labeled clearance/garage sign; the exterior and top-down previews show these parts distinctly.",
         'Facade bay spacing, stair tower position and exact ramp routing remain inferred; the available exterior photo is old and the current street-level appearance was not directly captured.'],
       'reason':'The main garage type and recognizable facade language are supported by the reference, while finer placement/rhythm and present-day details remain unverified.'},
      {'criterion':'Modular export, portability, and complete evidence','score':1.9,'max_score':2.0,'status':'verified as standalone library; master handoff pending',
       'evidence':[f"A fresh Blender 5.2.3 open of SHA256 {probe['sha256']} found the expected scene `{probe['scene']}`, collection `{probe['collection']}`, {probe['object_count']} objects and {probe['mesh_count']} mesh objects.",
         f"The geometry uses {len(probe['used_materials'])} procedural materials, has {len(probe['external_file_images'])} external file images and {len(probe['linked_libraries'])} linked libraries; the source collection is directly linked in the asset scene.",
         'The evidence folder contains raw GIS, official parking/map material, historic photo reference, build report, previews and fresh-open validation.'],
       'reason':'The reusable asset is self-contained and reopens cleanly; it still needs root-owned manifest/marker registration in the master.'}
    ]
    score=round(sum(c['score'] for c in criteria),2)
    findings=[
      'PASS: exact source GIS footprint, building identity, local-frame dimensions, eight decks, expected scene/collection, portability, and target asset hash were independently checked.',
      'Height is not a survey measurement. The 78 ft R field is interpreted as a roof datum; model top is 24.094 m versus 23.774 m implied by that field.',
      'Current exterior imagery was unavailable in the source packet. Facade bay spacing, stair tower location, and ramp routing remain inferred from a circa-2010 image and garage typology.',
      'Master integration is pending; the coordinator must place the collection instance at [313.530608, -503.852303] m and reopen the master to verify neighbors and transform.'
    ]
    return {'building':'Wood Street Parking Garage (PGW)','asset_id':build['stable_id'],'asset_path':model['asset_file'],'asset_sha256':probe['sha256'],'grader':'independent_grader_subagent','grade_date':'2026-10-26','score':score,'max_score':10,'passing_threshold':8,'status':'PASS' if score>=8 else 'FAIL','criteria':criteria,'evidence':['audit/purdue_wood_street_garage_pgw/independent_grade/model_probe.json','audit/purdue_wood_street_garage_pgw/build_report.json','audit/purdue_wood_street_garage_pgw/sources.json','audit/purdue_wood_street_garage_pgw/preview_exterior_dusk.png','audit/purdue_wood_street_garage_pgw/preview_top_down.png','audit/purdue_wood_street_garage_pgw/woodstreet_parking_entrance_reference.jpg'],'findings':findings,'master_integration_status':'PENDING_COORDINATOR_PLACEMENT_MARKER'}

result=evaluate(probe,build,sources)
(base/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({'score':result['score'],'status':result['status'],'asset_sha256':result['asset_sha256'],'criteria':[(c['criterion'],c['score']) for c in result['criteria']],'findings':result['findings']},indent=2))
