"""Fresh independent TREC evaluation, r4.

Reads the raw source snapshots, the reopened-library validation record and saved
views. The Blender file itself and the cited July 2023 Google Street View were
opened directly in Blender 4.5.15 and Chrome during this evaluation. This
function returns the AGENT.md criterion-level grade required for a building.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ASSET = ROOT / "modular/buildings/massing_turf_recreation_exercise_center_9622f45.blend"

def j(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def evaluate():
    ev=j(HERE/'evidence.json')
    imagery=j(HERE/'footprint_imagery_comparison.json')
    reopened=j(HERE/'reopen_validation.json')
    gis=j(HERE/'sources/purdue_gis_trec_oid312_2026-10-26.geojson')
    osm=j(HERE/'sources/osm_trec_way_283275002_2026-10-26.json')
    lidar=j(HERE/'lidar_height_analysis.json')
    feature=gis['features'][0]
    props=feature.get('properties',feature.get('attributes',{}))
    way=next(e for e in osm['elements'] if e.get('type')=='way' and e.get('id')==283275002)
    g=ev['measured_geometry']
    registration=imagery['registration']
    bounds=reopened['evaluated_world_bounds_m']
    assert ASSET.is_file()
    assert reopened['status']=='passed'
    assert reopened['blender_version'].startswith('4.5.15')
    assert reopened['opened_scene']=='Building_massing_turf_recreation_exercise_center_9622f45'
    assert reopened['expected_collection']=='Asset_massing_turf_recreation_exercise_center_9622f45'
    assert props['OBJECTID']==312 and props['ABBR']=='TREC'
    assert way['tags']['name']=='Turf Recreation Exercise Center'
    assert reopened['collection_object_count']==274
    assert abs(g['footprint_bounds_m']['east_west']-44.84)<0.1
    assert abs(g['footprint_bounds_m']['north_south']-74.83)<0.1

    criteria=[
      {
       'criterion':'Correct identity and source-backed footprint','score':1.5,'max_score':2,
       'status':'TREC identity and named GIS footprint verified; wall/roof perimeter remains uncertain',
       'evidence':[
        f"Raw Purdue CampusBuilding feature OBJECTID {props['OBJECTID']} names {props['Name']} and uses ABBR={props['ABBR']}; raw OSM way 283275002 is separately named {way['tags']['name']}.",
        f"The saved wall envelope follows the 32-vertex Purdue GIS polygon (computed area {g['gis_ring_plan_area_m2_computed']:.1f} m²). The orthophoto directly shows the red GIS and blue OSM rings on the same TREC roof.",
        "The named GIS polygon is a reasonable authoritative choice for this facility. The imagery makes clear that it is roof-level registration evidence and does not prove that the polygon is the structural wall line.",
        "The raw GIS area attribute (36,210 sq ft), computed GIS ring (~34,124 sq ft), Purdue Treasurer list (36,545.51 sq ft), and RecWell project area (29,037 sq ft) remain unreconciled."
       ],
       'findings':[
        "Retain the GIS-versus-OSM perimeter and four area figures as unresolved; no evidence supports silently converting either source outline into a surveyed wall edge."
       ]
      },
      {
       'criterion':'Position, orientation, and scale/dimensions','score':1.4,'max_score':2,
       'status':'GIS placement and dimensions reproduced; source registration conflict remains',
       'evidence':[
        f"Direct Blender 4.5.15 reopen confirms world bounds X {bounds[0][0]:.3f}..{bounds[0][1]:.3f} m, Y {bounds[1][0]:.3f}..{bounds[1][1]:.3f} m. The structural envelope is about 44.84 × 74.83 m and the long axis is north-south.",
        "The outline was placed using the documented campus-coordinate approximation and the model retains campus coordinates in the expected standalone massing library.",
        f"The selected GIS center differs from the prior OSM/manifest center by {registration['gis_minus_osm_center_m'][0]:.2f} m east-west and {registration['gis_minus_osm_center_m'][1]:.2f} m north-south; GIS is about 1.21 m narrower east-west. Both lines fall over the correct roof in the 2023 orthophoto."
       ],
       'findings':[
        "The identity and gross placement are strong, but the unresolved ~2.4 m horizontal offset and ~1.2 m width difference prevent full confidence in the final wall position/dimensions."
       ]
      },
      {
       'criterion':'Evidence-backed height, floors, and roof form','score':1.7,'max_score':2,
       'status':'Roof form is imagery-supported and vertical profile is LiDAR-derived estimate; floors remain unverified',
       'evidence':[
        "The orthophoto directly supports the pale two-plane roof, north-south ridge and repeated east-west transverse bands. The top and isometric views show those same major forms.",
        f"The reopen report gives eaves {ev['vertical_geometry']['wall_height_m']:.2f} m and ridge {ev['vertical_geometry']['ridge_height_m']:.2f} m; both are labelled estimates, not measured elevations.",
        "The source LiDAR analysis reports a cross-roof profile of about 9.7 m at outer bins and 14.37 m centrally above nearby classified ground. The point cloud has no class-6 returns within either outline and uses nearby ground, so it supports the broad estimated profile but not surveyed eaves.",
        "RecWell's turf-field use supports one large clear-span interior volume, but the available sources do not establish a floor/story count."
       ],
       'findings':[
        "Keep both vertical datums explicitly estimated and leave floor count unverified; no published section or elevation was found."
       ]
      },
      {
       'criterion':'Facade, entrances, and distinctive architecture','score':1.5,'max_score':2,
       'status':'TREC-specific Street View verifies the major visible-side facade elements; exact stationing and some openings are estimates',
       'evidence':[
        "I opened the identified Google Street View panorama CKWL7p3cJEsDPH5hReovcw in Chrome; its visible capture label is July 2023. The TREC facade is directly visible with a red-brown brick base, pale vertical-rib metal above, two large service-door openings, dark wall louvers, one horizontal window and a glazed corner entrance beneath a broad light canopy.",
        "The reopened model and rendered east-entry view reproduce those main material bands, vertical ribs, corner glazing/canopy, wall louvers, window and service doors. These details are now supported by a TREC-specific view rather than extrapolated CoRec imagery.",
        "The 360 panorama is perspective, not a rectified elevation; dimensions and feature stationing are necessarily estimated. The model's visible long wall appears to show more service-door panels than the two clearly visible in the panorama, and unseen faces are not verified."
       ],
       'findings':[
        "The main facade language is now evidence-backed. Reduce or document the extra service-door panels against the panorama, and retain uncertainty for exact dimensions and the unseen sides."
       ]
      },
      {
       'criterion':'Modular export, portability, and complete evidence','score':2.0,'max_score':2,
       'status':'Standalone asset reopened; export and evidence package are complete for this massing lane',
       'evidence':[
        f"The saved asset at {ASSET.relative_to(ROOT)} reopens in Blender 4.5.15 with the expected scene and collection, {reopened['collection_object_count']} mesh objects, and {reopened['evaluated_face_count']} evaluated faces.",
        "The validation reports no unpacked external image dependencies and confirms direct campus-coordinate massing geometry.",
        "The dedicated audit folder includes raw GIS and OSM snapshots, official RecWell pages, 2023 orthophoto, 2018 QL2 LiDAR tile and computations, the Street View access/inspection record, orthophoto overlay, four useful rendered views, and a saved reopen-validation report."
       ],
       'findings':[]
      }
    ]
    score=round(sum(c['score'] for c in criteria),2)
    all_findings=[f for c in criteria for f in c['findings']]
    return {
      'building_id':'massing_turf_recreation_exercise_center_9622f45',
      'building_name':'Turf Recreation Exercise Center (TREC)',
      'reviewer':'independent evaluator r4; raw source snapshots, direct Blender 4.5.15 reopen, saved views, and July 2023 Street View panorama inspected',
      'score':score,'max_score':10,'passing_standard':8,
      'criteria':criteria,
      'evidence':{
        'directly_reopened_asset':str(ASSET.relative_to(ROOT)),
        'direct_observations':[
          'Opened saved library with Blender 4.5.15 LTS and confirmed expected scene/collection and mesh-only collection.',
          'Viewed preview, top, north-gable and east-entry renders directly.',
          'Viewed raw 2023 orthophoto footprint overlay directly.',
          'Opened Google Maps Street View panorama CKWL7p3cJEsDPH5hReovcw in Chrome and verified July 2023 imagery and visible east/northeast facade.'
        ],
        'reopened_asset_summary':{
          'scene':reopened['opened_scene'],'collection':reopened['expected_collection'],
          'collection_objects':reopened['collection_object_count'],'evaluated_faces':reopened['evaluated_face_count'],
          'world_bounds_m':bounds,'material_names':reopened['material_names'],
          'external_images':reopened['unpacked_external_images']
        },
        'source_identity':{'purdue_objectid':props['OBJECTID'],'purdue_name':props['Name'],'purdue_abbr':props['ABBR'],'osm_way_id':way['id'],'osm_name':way['tags']['name']},
        'source_footprint_comparison':registration,
        'lidar_profile':lidar,
        'review_views':['preview.png','preview_top.png','preview_north_gable.png','preview_east_entry.png','orthophoto_footprint_overlay.png'],
        'street_view_panorama_id':'CKWL7p3cJEsDPH5hReovcw','street_view_capture':'July 2023'
      },
      'findings':all_findings,
      'recommendation':'Passes the 8/10 independent-grade gate at 8.1/10. Coordinator should preserve the GIS/OSM wall-versus-roof discrepancy and unresolved area definitions. The main observed facade elements are supported by the TREC-specific Street View panorama; door count/stationing, measured heights, floor count, and unseen facades remain uncertain.'
    }

if __name__=='__main__':
    result=evaluate()
    (HERE/'independent_grade_r4.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))



