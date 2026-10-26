import hashlib, json, math
from pathlib import Path
from shapely.geometry import Polygon
ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/'modular/buildings/massing_first_street_towers_east_fste_c9b22d3.blend'
PROBE=Path(__file__).with_name('candidate_probe.json')
GEO=ROOT/'audit/first_street_towers_east/sources/purdue_buildingshapeszip4_fste_fid651_2026-10-26.geojson'
EVID=ROOT/'audit/first_street_towers_east/evidence.md'
MANIFEST=ROOT/'modular/manifest.json'
EXPECTED='488cf1dd2775afb78b6de7badc06a588f1be036bb87eda8428b7db30ffb9dcb2'

def local_xy(lon,lat):
    return ((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0)

def main():
    actual=hashlib.sha256(ASSET.read_bytes()).hexdigest()
    p=json.loads(PROBE.read_text(encoding='utf-8'))
    geo=json.loads(GEO.read_text(encoding='utf-8'))
    assert actual==EXPECTED, f'Candidate changed: {actual}'
    assert p['candidate_sha256']==EXPECTED and p['fresh_process_opened']
    f=next(x for x in geo['features'] if x.get('properties',{}).get('FID')==651)
    props=f['properties']
    src=Polygon([local_xy(lon,lat) for lon,lat in f['geometry']['coordinates'][0]])
    mod=Polygon([tuple(xy) for xy in p['base_outline_xy_m']])
    inter=src.intersection(mod).area
    union=src.union(mod).area
    iou=inter/union
    h=float(src.hausdorff_distance(mod))
    m=json.loads(MANIFEST.read_text(encoding='utf-8'))
    row=next(x for x in m['assets'] if x.get('id')=='massing_first_street_towers_east_fste_c9b22d3')
    criteria=[
      {'name':'Correct identity and source-backed footprint','score':2.0,'max_score':2,
       'evidence':[f"Purdue GIS FID 651 identifies BLDG_ABBR={props['BLDG_ABBR']}, BUILDING_N={props['BUILDING_N']}, address {props['ADDRESS']}.",f"Independent local-projection comparison: source area {src.area:.3f} m²; candidate {mod.area:.3f} m²; IoU {iou:.6f}; Hausdorff {h:.3f} m."],
       'finding':'Strong source identity and footprint match. Source GIS snapshot is direct evidence.'},
      {'name':'Position, orientation, and scale/dimensions','score':2.0,'max_score':2,
       'evidence':[f"Candidate source-aligned bounds {mod.bounds}; independent source bounds {src.bounds}.","Model uses project approximate lon/lat-to-campus XY transform; dimensions agree with the same source polygon."],
       'finding':'Footprint alignment, orientation, and plan scale are directly verified within the documented approximate campus transform; this is not survey-grade georeferencing.'},
      {'name':'Evidence-backed height, floors, and roof form','score':0.9,'max_score':2,
       'evidence':[f"GIS NUM_LEVELS={props.get('NUM_LEVELS')} and CountOfFLO={props.get('CountOfFLO')} support six levels.",f"Candidate floor plates occur at Z={p['floor_plate_z_m']}; highest overall modeled Z={p['world_bounds_xyz_m'][2][1]:.2f} m."],
       'finding':'Six levels are supported, but story spacing and 19.9 m total height are estimates. GIS Extrution=52 is undocumented and cannot verify height. Flat roof and parapet have no tower-specific plan/photo support; the Purdue photo is complex-wide and visibly includes peaked roof masses, so candidate roof fidelity is unresolved.'},
      {'name':'Facade, entrances, and distinctive architecture','score':0.9,'max_score':2,
       'evidence':["The Purdue photo shows warm masonry, regular light-framed windows, and distinct entry glazing at complex level.","Exterior render shows repeated windows, pale horizontal bands, warm brick, a plain roof, and no modeled/verified entrance."],
       'finding':'General brick/window language is plausible from the complex photo, but FSTE-specific facade bay rhythm is not established. The model omits a verified entrance and distinctive roof/entry features; source image cannot establish which complex wing corresponds to this GIS footprint.'},
      {'name':'Modular export, portability, and complete evidence','score':1.3,'max_score':2,
       'evidence':[f"Fresh Blender 5.2.3 process opened exact SHA; export collection {p['collection']} contains {p['object_count']} objects / {p['mesh_count']} meshes and {p['material_count']} materials.",f"No external images, linked libraries, or invalid meshes: images={p['external_images']}, libraries={p['linked_libraries']}, invalid={p['invalid_meshes']}.","Building-specific evidence contains source snapshots, exterior and top renders, measurement method, and uncertainty notes."],
       'finding':f"Asset is portable and opens cleanly, but shared manifest is stale (records object_count={row.get('object_count')} and Z bounds {row.get('bounds_world_m',[[],[],[]])[2]}, versus fresh asset {p['object_count']} objects and Z=[{p['world_bounds_xyz_m'][2][0]:.2f}, {p['world_bounds_xyz_m'][2][1]:.2f}] m). The interior is schematic rather than a verified plan; no interior/cutaway view is supplied."}
    ]
    score=round(sum(c['score'] for c in criteria),1)
    result={'building_id':'massing_first_street_towers_east_fste_c9b22d3','asset_path':str(ASSET),'candidate_sha256_expected':EXPECTED,'candidate_sha256_verified':actual,'fresh_opened_in_blender':p['fresh_process_opened'],'score':score,'max_score':10,'passing_threshold':8,'status':'PASS' if score>=8 else 'FAIL','criteria':criteria,'evidence':{'source':'Purdue BuildingShapesZip4 FeatureServer layer 0, FID 651; EPSG:4326; snapshot retrieved 2026-10-26','source_geometry_valid':src.is_valid,'candidate_geometry_valid':mod.is_valid,'footprint_metrics':{'source_area_m2':round(src.area,4),'candidate_area_m2':round(mod.area,4),'area_difference_m2':round(mod.area-src.area,4),'intersection_over_union':round(iou,6),'hausdorff_m':round(h,4),'source_bounds_xy_m':[round(x,4) for x in src.bounds],'candidate_bounds_xy_m':[round(x,4) for x in mod.bounds]},'visuals':['audit/first_street_towers_east/fste_exterior_candidate.png','audit/first_street_towers_east/fste_footprint_top_candidate.png','audit/first_street_towers_east/sources/first_street_towers_exterior_official_640x360.jpg'],'fresh_probe':'audit/first_street_towers_east_independent_grade/candidate_probe.json'},'findings':['Strong GIS identity, placement, and plan footprint match.','Floor count is supported, but height, story spacing, and roof are not independently confirmed for the East tower.','Facade is plausible at complex level but the render lacks a verified entrance and tower-specific architectural features.','The candidate itself opens and has portable materials; the shared manifest metadata is stale and should be reconciled before integration.'],'methodology':'Independent fresh-open structural inspection plus planar Shapely comparison using project local XY conversion. Visual scoring uses candidate render and available official Purdue complex-level photo. Unsupported height, roof, and interior details were treated as uncertain. No builder score or appearance-only claim was used.'}
    out=Path(__file__).with_name('result.json')
    out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'score':score,'status':result['status'],'sha256':actual,'footprint':result['evidence']['footprint_metrics']},indent=2))
if __name__=='__main__': main()
