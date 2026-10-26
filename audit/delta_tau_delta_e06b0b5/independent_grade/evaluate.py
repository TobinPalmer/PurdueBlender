#!/usr/bin/env python3
"""Independent rubric evaluator for Delta Tau Delta (not a builder-authored claim checker)."""
from __future__ import annotations
import json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / 'audit' / 'delta_tau_delta_e06b0b5'
ASSET_REOPEN = AUDIT / 'independent_grade' / 'reopen_inspection.json'
GIS = AUDIT / 'sources' / 'indiana_lidar_building_footprint_oid409940_2026-10-26.json'
SOURCES = AUDIT / 'sources' / 'documentary_sources_snapshot_2026-10-26.json'
EVIDENCE = AUDIT / 'build_evidence.json'

def project(lon, lat):
    lat0, lon0 = 40.4274, -86.9137
    return ((lon-lon0)*111412.84*math.cos(math.radians(lat0)), (lat-lat0)*111040.0)

def evaluate():
    reopen=json.loads(ASSET_REOPEN.read_text(encoding='utf-8-sig'))
    gis=json.loads(GIS.read_text(encoding='utf-8-sig'))
    src=json.loads(SOURCES.read_text(encoding='utf-8-sig'))
    be=json.loads(EVIDENCE.read_text(encoding='utf-8-sig'))
    ring=gis['features'][0]['geometry']['rings'][0][:-1]
    expected=[project(lon,lat) for lon,lat in ring]
    body=reopen['structural_body']
    actual=[(v[0],v[1]) for v in body['world_vertices_xyz'] if abs(v[2]) < 1e-5]
    # Symmetric nearest-vertex distance; the geometry represents a straight-sided ring.
    d1=[min(math.dist(p,q) for q in actual) for p in expected]
    d2=[min(math.dist(q,p) for p in expected) for q in actual]
    hausdorff=max(d1+d2)
    source_ids=[s.get('feature_id','') for s in src['sources']]
    external=reopen['external_libraries']
    all_mods=sum(len(o['modifiers']) for o in reopen['objects'])
    score_items=[
      {'criterion':'Correct identity and source-backed footprint','points':1.75,'max_points':2,
       'evidence':f"Directly compared 6 transformed vertices from 2018 Indiana LiDAR objectid 409940 with the reopened shell's six base vertices; symmetric nearest-vertex max difference {hausdorff:.6f} m. Address 400 Northwestern, 1928 construction, and the fraternity shelter are corroborated by the zoning report and 1970 chapter publication. The GIS feature itself is unlabeled and the address point falls just outside the polygon.",
       'finding':'Footprint match is excellent; identity remains a spatial/documentary association rather than a named survey feature.'},
      {'criterion':'Position, orientation, and scale/dimensions','points':2.0,'max_points':2,
       'evidence':f"Reopened campus-coordinate structural XY bounds are {body['bounds_world_m'][0][0]:.4f}–{body['bounds_world_m'][0][1]:.4f} m east and {body['bounds_world_m'][1][0]:.4f}–{body['bounds_world_m'][1][1]:.4f} m north; they agree with the transformed GIS ring. Asset preserves campus coordinates and expected collection.",
       'finding':'No material horizontal position, orientation, or scale discrepancy found.'},
      {'criterion':'Evidence-backed height, floors, and roof form','points':1.0,'max_points':2,
       'evidence':'The zoning staff report identifies Tudor Revival characteristics, which supports a steep roof silhouette at a broad stylistic level. The model records 10.4 m eaves, 15.2 m ridge, 17.4 m chimney tops, three window bands, and three chimneys as estimates. Reviewed sources contain no measured elevations or floor plan; exact heights, floor count, roof geometry, and chimney count are unsupported.',
       'finding':'Retain the estimated labels; obtain a dimensioned elevation/plan or directly inspected archival photo set to verify height, floors, roof and stacks.'},
      {'criterion':'Facade, entrances, and distinctive architecture','points':1.0,'max_points':2,
       'evidence':'The sources support red brick and a general Tudor Revival character only weakly: the X profile is a small, cropped seasonal image, while the 2021 report names the style. The rendered asset shows repeated window panels, lintels, a west-side entry, projecting gable/canopy, and a regular side rhythm. The source snapshot says archival negatives and photos exist but were not inspected; no facade drawing, measured entry, window count, or 1970 addition junction was found.',
       'finding':'The visual massing is coherent but most facade placement/detail is schematic. Verify the actual elevations and 1970 addition from archival imagery, or simplify unsupported detail.'},
      {'criterion':'Modular export, portability, and complete evidence','points':1.5,'max_points':2,
       'evidence':f"Blender {reopen['blender_version']} reopened the saved file. Expected scene/collection are present; {reopen['object_count']} mesh objects are in the scene and target collection, there are {all_mods} modifiers, and external linked libraries are {len(external)}. Structured source/build evidence and both saved preview images are present. The three-quarter render is inspectable. The plan render is clipped vertically by the orthographic framing and mostly shows the roof; the shared manifest currently still lists one object and original bounds, inconsistent with the reopened 73-object asset.",
       'finding':'Library is portable and opens correctly; repair the plan framing and ask the coordinator to refresh the manifest/index count and bounds before integration.'}
    ]
    score=round(sum(c['points'] for c in score_items),2)
    return {'score':score,'max_score':10,'criteria':score_items,
      'evidence':{
        'asset_reopen':{'path':str(Path(reopen['asset']).relative_to(ROOT)),'sha256':reopen['sha256'],'blender_version':reopen['blender_version'],'scene':reopen['scene'],'collection':'Asset_massing_delta_tau_delta_e06b0b5','object_count':reopen['object_count'],'bounds_world_m':reopen['bounds_world_m'],'external_libraries':external,'modifiers_total':all_mods},
        'footprint_check':{'provider':'Indiana Building Footprints, Tippecanoe County 2018 LiDAR','feature_id':409940,'transformed_source_vertex_count':len(expected),'reopened_shell_bottom_vertex_count':len(actual),'symmetric_nearest_vertex_max_error_m':round(hausdorff,8),'shape_area_m2':gis['features'][0]['attributes']['SHAPE__Area'],'shape_perimeter_m':gis['features'][0]['attributes']['SHAPE__Length']},
        'documentary_source_ids':source_ids,
        'previews':['audit/delta_tau_delta_e06b0b5/previews/delta_tau_delta_three_quarter.png','audit/delta_tau_delta_e06b0b5/previews/delta_tau_delta_plan.png'],
        'direct_image_inspection':'Three-quarter view shows a simple brick envelope, very broad roof planes, three stacks, repeated window panels and schematic entrance. Plan preview crops the north/south extent and is dominated by roof; it is not a reliable footprint presentation.'},
      'findings':['Score is below the 8/10 threshold.','Footprint/XY are accurately derived from an unlabeled 2018 GIS polygon, but identity is inferential.','No measured vertical data or directly reviewed facade/elevation record is present; the documented construction-era photo/plan leads have not been inspected.','Plan preview framing and stale shared manifest need coordinator follow-up.']}

if __name__=='__main__':
    out=evaluate()
    (AUDIT/'independent_grade'/'result.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(out,indent=2,ensure_ascii=False))
