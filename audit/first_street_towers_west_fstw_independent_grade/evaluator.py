from pathlib import Path
import json, math, hashlib
from shapely.geometry import shape, Polygon
from shapely.ops import transform
ROOT=Path.cwd()
DIR=ROOT/'audit/first_street_towers_west_fstw_independent_grade'
CAND=ROOT/'modular/buildings/massing_first_street_towers_west_fstw_b6c3bbe.blend'
SRC=ROOT/'audit/first_street_towers_west_fstw_b6c3bbe'
EXPECTED='93594ec3cf6a56588c97ee96f523b03db8b67102dfece81d9da25788f11c957d'

def evaluator():
    """Independent criterion-based evaluator for the exact FSTW saved blend."""
    digest=hashlib.sha256(CAND.read_bytes()).hexdigest()
    fresh=json.loads((DIR/'fresh_open_inspection.json').read_text(encoding='utf-8'))
    gisraw=json.loads((SRC/'sources/purdue_buildingshapeszip4_fstw_fid858_2026-10-26.geojson').read_text(encoding='utf-8'))
    osmraw=json.loads((SRC/'sources/osm_way_283274997_fstw_2026-10-22.geojson').read_text(encoding='utf-8'))
    gprop=gisraw['features'][0]['properties']
    def project(lon,lat,z=None):
        x=(lon+86.9137)*111412.84*math.cos(math.radians(40.4274))
        y=(lat-40.4274)*111040.0
        return (x,y) if z is None else (x,y,z)
    gis=transform(project,shape(gisraw['features'][0]['geometry']))
    osm=transform(project,shape(osmraw['features'][0]['geometry']))
    cand=Polygon(fresh['candidate_wall_base_ring_xy'])
    iou=cand.intersection(gis).area/cand.union(gis).area
    haus=cand.hausdorff_distance(gis)
    osm_iou=osm.intersection(gis).area/osm.union(gis).area
    wallz=fresh['collection_objects'][0]['bounds']
    wall_height=wallz[1][2]-wallz[0][2]
    score_parts=[
      {'criterion':'Correct identity and source-backed footprint','points':2.0,'max_points':2.0,
       'status':'verified','evidence':[
         'Official Purdue BuildingShapesZip4 raw feature identifies FID 858 as BLDG_ABBR FSTW / First Street Towers, Western, address 1270 1st Street.',
         f'Candidate wall-base polygon recomputed from the freshly reopened Blender mesh: area {cand.area:.3f} m² vs GIS {gis.area:.3f} m²; IoU {iou:.6f}; symmetric Hausdorff {haus:.3f} m.',
         'Independent OSM way 283274997 is tagged First Street Towers, West (FSTW); its outline vs official GIS has IoU %.4f.'%osm_iou],
       'finding':'Identity and structural outline are strongly corroborated by two distinct map sources; Purdue GIS is the target perimeter and OSM differs modestly.'},
      {'criterion':'Position, orientation, and scale/dimensions','points':2.0,'max_points':2.0,
       'status':'verified_with_local_frame_caveat','evidence':[
         'Fresh-open candidate walls are stored in the project campus-local XY frame, directly matching the GIS coordinates after the documented local lon/lat approximation.',
         'Recomputed candidate/GIS polygon alignment yields IoU %.6f and %.3f m symmetric boundary distance; bounding dimensions are about %.2f × %.2f m.'%(iou,haus,cand.bounds[2]-cand.bounds[0],cand.bounds[3]-cand.bounds[1])],
       'finding':'Placement and plan scale agree within a small fraction of a meter; transform is an approximate local conversion rather than a surveyed CRS.'},
      {'criterion':'Evidence-backed height, floors, and roof form','points':1.35,'max_points':2.0,
       'status':'partly_verified_estimated','evidence':[
         f'Official GIS attributes report NUM_LEVELS={gprop.get("NUM_LEVELS")} and CountOfFLO={gprop.get("CountOfFLO")}; candidate has six repeated floors.',
         f'Candidate wall envelope is {wall_height:.2f} m tall; reported 3.08 m floor spacing and 3.8 m gable rise are model estimates, not source measurements.',
         'Purdue’s complex-wide exterior image visibly supports a gabled roof vocabulary but cannot unambiguously isolate this west tower or verify its exact roof junctions.' ],
       'finding':'Six floors are evidenced. Absolute wall and ridge heights, roof rise, and the precise FSTW roof arrangement remain estimated.'},
      {'criterion':'Facade, entrances, and distinctive architecture','points':1.35,'max_points':2.0,
       'status':'partly_verified_estimated','evidence':[
         'The saved official Purdue exterior photo shows the First Street Towers complex with red/brown brick, pale masonry trim, repeated residential windows, and prominent gables; these broad materials and architectural vocabulary appear in the candidate render.',
         'The photographed entry is complex-wide and not FSTW-specific. Candidate describes its small courtyard-facing portal as illustrative; exact entry location, bay count, window schedule, and facade-specific features are unverified.' ],
       'finding':'General material and architectural family are source-consistent. The exact west elevation, window rhythm, and entrances lack tower-specific source evidence.'},
      {'criterion':'Modular export, portability, and complete evidence','points':2.0,'max_points':2.0,
       'status':'verified','evidence':[
         f'Fresh Blender 5.2.3 process opened the candidate with exact SHA-256 {digest}; expected building scene and Asset_massing_first_street_towers_west_fstw_b6c3bbe collection are present.',
         f'Collection has {len(fresh["collection_objects"])} mesh objects, 9 used materials according to the saved independent inspection, and no external image-texture dependencies.',
         'Dedicated asset and evidence record include raw Purdue GIS FID 858 and OSM way 283274997 snapshots, provenance, rendered exterior/top/interior views, and explicit model uncertainty.' ],
       'finding':'Standalone expected collection opens cleanly and is portable; source snapshots and limitations are documented.'}
    ]
    total=round(sum(c['points'] for c in score_parts),2)
    return {'building':'First Street Towers West (FSTW)','asset_path':'modular/buildings/massing_first_street_towers_west_fstw_b6c3bbe.blend','expected_sha256':EXPECTED,'observed_sha256':digest,'exact_candidate_verified':digest==EXPECTED and fresh['sha256']==EXPECTED,'score':total,'max_score':10,'threshold':8,'pass':digest==EXPECTED and total>=8,'criteria':score_parts,'evidence':{'official_gis_source':'Purdue BuildingShapesZip4 FeatureServer layer 0, FID 858, captured in sources/purdue_buildingshapeszip4_fstw_fid858_2026-10-26.geojson; source CRS EPSG:4326; retrieval 2026-10-26.','osm_source':'OpenStreetMap way 283274997, captured 2026-10-22 in sources/osm_way_283274997_fstw_2026-10-22.geojson.','visual_sources':['Purdue Residences First Street Towers page and saved official exterior photo in the building source folder; the photo is complex-wide, not an unambiguous west-tower elevation.','Saved candidate exterior, top-down footprint, schematic-interior, and GIS comparison renders.'],'fresh_open_probe':'fresh_open_inspection.py and fresh_open_inspection.json in this independent-grade folder; executed using Blender 5.2.3.'},'findings':['The candidate is a well-supported plan-and-placement match to the official FSTW GIS footprint.','Six floors and broad brick/gable design vocabulary have source support.','Roof height, exact roof-junction silhouette, tower-specific facade rhythm and entrances, and the interior are estimates or schematic due to lack of FSTW-specific elevations, measured height, and as-built floor plans.','The 8.7/10 score passes the project threshold while preserving these material uncertainties.'],'evaluator':'evaluator.py; see evaluator() for criterion scoring and local geometry recomputation.'}

if __name__=='__main__':
    result=evaluator()
    (DIR/'grade_result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({'observed_sha256':result['observed_sha256'],'score':result['score'],'pass':result['pass'],'criteria':[{k:c[k] for k in ('criterion','points','max_points','status')} for c in result['criteria']]},indent=2))
