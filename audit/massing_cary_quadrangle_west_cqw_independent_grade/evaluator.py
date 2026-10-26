"""Independent CQW evaluator. Run with: python evaluator.py"""
import json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
ID='massing_cary_quadrangle_west_cqw_3d47a7d'
AUDIT=Path(__file__).resolve().parent
ASSET=ROOT/'modular'/'buildings'/f'{ID}.blend'
SOURCE=ROOT/'audit'/ID/'sources'

def evaluate():
    probe=json.loads((AUDIT/'blender_probe.json').read_text(encoding='utf8'))
    src=json.loads((SOURCE/'purdue_cary_quadrangle_west_*.json').read_text(encoding='utf8')) if False else json.loads((SOURCE/'purdue_cqw_fid60_wgs84.geojson').read_text(encoding='utf8'))
    feat=src['features'][0]; prop=feat['properties']; ring=feat['geometry']['coordinates'][0]
    pts=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0) for lon,lat in ring]
    if pts[0]==pts[-1]: pts.pop()
    area=abs(sum(pts[i][0]*pts[(i+1)%len(pts)][1]-pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts)))/2)
    sb=probe['shell_xy_bounds_m']
    source_bounds=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(2)]
    bounds_delta=max(abs(sb[i][j]-source_bounds[i][j]) for i in range(2) for j in range(2))
    export_ok=(probe['scene']==f'Building_{ID}' and probe['collection']==f'Asset_{ID}' and probe['mesh_count']>0 and not probe['external_dependencies'])
    criteria=[
      {'name':'Correct identity and source-backed footprint','score':2.0,'max_score':2.0,
       'evidence':f"Purdue GIS FID {prop['FID']} identifies {prop['BUILDING_N']} (CQW), matching Purdue Archives building record 10 / structure 116. Reprojected GIS polygon area is {area:.1f} m²; saved shell XY bounds differ from the independent transformed source bounds by at most {bounds_delta:.4f} m. Shell has 0 boundary and 0 nonmanifold edges.",
       'findings':'Identity and plan polygon are directly source-backed. GIS service does not provide survey tolerance or prove that its building outline is the exact masonry wall line.'},
      {'name':'Position, orientation, and scale/dimensions','score':2.0,'max_score':2.0,
       'evidence':f"The saved shell follows the source GIS coordinates in the repository's documented approximate local campus transform, with maximum XY bounds residual {bounds_delta:.4f} m. The asset remains in campus coordinates as required for massing; footprint outline and cardinal orientation agree with GIS.",
       'findings':'The main shell is correctly located and scaled to the GIS outline. Tower, oriel, and entrance projections extend beyond that shell; archival images support their existence but do not quantify their projection.'},
      {'name':'Evidence-backed height, floors, and roof form','score':1.25,'max_score':2.0,
       'evidence':f"Purdue GIS records NUM_LEVELS={prop['NUM_LEVELS']} and Extrution={prop['Extrution']}; the asset represents five levels. Fresh Blender 4.5.15 reopen measured body top around 14.63 m and tallest tower top {probe['evaluated_bounds_m'][2][1]:.2f} m. Purdue Archives photos 180–182 support a mostly flat/parapeted roof and taller twin entrance towers.",
       'findings':'The vertical extrusion unit is undocumented. The 14.63 m body assumes 48 feet; tower height and floor-to-floor spacing are estimates with no measured elevation source. Roof form is qualitative only.'},
      {'name':'Facade, entrances, and distinctive architecture','score':1.0,'max_score':2.0,
       'evidence':'The saved render contains a five-row window rhythm, brick/stone palette, paired towers, central projecting oriel and three entrance locations. Purdue Archives image 180 (1950s) shows two taller, more articulated towers, a prominent Gothic central entrance, flanking pointed-arch entrances, and distinct roof/crown details; image 181 (2004) independently shows the twin-tower entry and projecting central bay.',
       'findings':'The model translates those motifs into rectangular block towers and simplified trim. The central entrance is mostly a rectangular dark opening with angular trim rather than the clearly pointed Gothic arch in the 1950s source; tower upper profiles, masonry articulation, and the specific window groupings are not well matched. The archive photos are oblique/frontal and do not support exact dimensions.'},
      {'name':'Modular export, portability, and complete evidence','score':1.25,'max_score':2.0,
       'evidence':f"Fresh reopen confirms scene {probe['scene']}, collection {probe['collection']}, {probe['mesh_count']} mesh objects, saved evaluated bounds, and no missing external images or linked libraries. The .blend re-renders successfully. Raw Purdue GIS metadata/feature, GeoJSON, Archives record HTML/JSON, and source photographs are preserved with URL/date/CRS and uncertainty notes.",
       'findings':'Asset path and collection name match the manifest, but the manifest entry still describes one object named Cary Quadrangle West (CQW), old bounds, and 16 m top height; the current asset has 1,628 meshes and reaches 19.30 m. The coordinator should refresh the shared manifest/index after building acceptance. This evaluator did not edit shared files.'}
    ]
    score=round(sum(c['score'] for c in criteria),2)
    result={'asset_id':ID,'asset_path':f'modular/buildings/{ID}.blend','grader':'independent subagent','evaluated_on':'2026-10-26','score':score,'max_score':10,'passing_threshold':8,'passed':score>=8,'criteria':criteria,'evidence':{'fresh_blender_probe':'blender_probe.json','fresh_blender_log':'blender_probe.log','fresh_reopen_render':'fresh_reopen_render.png','raw_source_index':f'audit/{ID}/sources/source_index.json','raw_gis_feature':f'audit/{ID}/sources/official_feature_60_raw.json','raw_gis_geojson':f'audit/{ID}/sources/purdue_cqw_fid60_wgs84.geojson','purdue_archives_record':f'audit/{ID}/sources/purdue_historic_building_10_record.json','source_images':[f'audit/{ID}/sources/purdue_earchives_image_{n}_'+label for n,label in [(180,'external_shot_of_cary_quad_resid.jpg'),(181,'exterior_photograph_of_cary_hall.jpg'),(182,'exterior_photograph_of_cary_hall.jpg')]],'gis_polygon_area_local_approx_m2':round(area,3),'shell_bounds_max_residual_m':round(bounds_delta,5)},'findings':['The GIS identity and footprint are strong; measured shell outline agrees with the transformed polygon.','Height remains estimated because the GIS Extrution units are undocumented and no measured elevation is present.','Improve the central pointed arch and tower silhouette/detail against the direct Purdue Archives references.','Refresh shared manifest metadata to match the accepted current asset; coordinator-owned files were not changed.']}
    (AUDIT/'result.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps(result,indent=2))
    return result

if __name__=='__main__': evaluate()

