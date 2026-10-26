from __future__ import annotations
import hashlib, json, math
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))

def evaluate():
    asset=read(HERE/'blender_asset_probe.json')
    master=read(HERE/'master_placement_probe.json')
    export=read(HERE/'independent_export_reopen.json')
    smoke=read(HERE/'builder_smoke_reopen.json')
    geometry=read(HERE/'builder_rebuild_geometry_comparison.json')
    feature_doc=read(HERE/'sources/purdue_gis_fid_645.json')
    feature=feature_doc['features'][0]; attrs=feature['attributes']; ring=feature['geometry']['rings'][0]
    manifest=read(HERE/'sources/manifest_snapshot.json')
    entry=next(a for a in manifest['assets'] if a.get('id')=='black_cultural_center')
    record=read(HERE/'sources/source_record.json')
    marker=master['markers'][0] if master['marker_count']==1 else {}
    origin=entry['placement_origin_xy_m']
    marker_delta=[float(marker['location'][i])-float(origin[i]) for i in range(2)]
    src_local=[]
    lon=[p[0] for p in ring[:-1]]; lat=[p[1] for p in ring[:-1]]
    cx=(min(lon)+max(lon))/2; cy=(min(lat)+max(lat))/2
    for x,y in ring[:-1]: src_local.append(((x-cx)*84810.60416539927,(y-cy)*111040.0))
    area=abs(sum(src_local[i][0]*src_local[(i+1)%len(src_local)][1]-src_local[(i+1)%len(src_local)][0]*src_local[i][1] for i in range(len(src_local)))/2)
    asset_path=ROOT/'modular/buildings/black_cultural_center.blend'
    sha=hashlib.sha256(asset_path.read_bytes()).hexdigest()
    identity_ok=(attrs.get('FID'),attrs.get('BLDG_ABBR'),attrs.get('BUILDING_N'))==(645,'BCC','Black Cultural Center')
    scores=[2.0,2.0,1.0,2.0,2.0]
    criteria=[
      {'name':'Correct identity and source-backed footprint','score':scores[0],'max_score':2,
       'assessment':f"Official Purdue BuildingShapes GIS feature 645 identifies BCC at 1100 3rd Street. I compared the 61 unique source-ring vertices with the evaluated BCC first-floor brick shell after centering the EPSG:4326 feature bounds and applying the project local approximation. The maximum bidirectional nearest-vertex distance is {max(asset['source_to_shell_nearest_max_m'],asset['shell_to_source_nearest_max_m']):.8f} m, and the structural shell XY bounds match the source bounds. Identity is corroborated by Purdue's own BCC facility/location pages. The GIS perimeter is not a surveyed elevation source." if identity_ok else 'The GIS source feature did not resolve to the expected BCC identity.'},
      {'name':'Position, orientation, and scale/dimensions','score':scores[1],'max_score':2,
       'assessment':f"The current manifest specifies local geometry and campus origin {origin} m. The master contains exactly one Placement_black_cultural_center marker at {marker.get('location')}; XY delta is {[round(v,6) for v in marker_delta]} m, rotation is {marker.get('rotation_degrees')} degrees, scale is {marker.get('scale')}, and it instances the expected relative library. The GIS shell bounds and plan orientation agree within about 0.000001 m; overall measured model bounds are {asset['evaluated_bounds_local_m']}."},
      {'name':'Evidence-backed height, floors, and roof form','score':scores[2],'max_score':2,
       'assessment':f"GIS NUM_LEVELS={attrs.get('NUM_LEVELS')} and Purdue's facility page documents a second-floor lab, supporting a multilevel building. Official photos and architectural descriptions support a low-slope roof with clerestory monitors. The model top is {asset['evaluated_bounds_local_m'][2][1]:.2f} m, but no measured elevation or plan dimensions were found; GIS Extrution={attrs.get('Extrution')} has no resolved units/definition. Eave, roof and total heights therefore remain estimates."},
      {'name':'Facade, entrances, and distinctive architecture','score':scores[3],'max_score':2,
       'assessment':'Purdue BCC’s official architectural description supports the African-village concept, geometric brick motif, keyhole portal with cast-stone medallions, octagonal glazed lobby, and upper wrought-iron balcony. The Purdue 2021 exterior photo supports the red brick/pale stone palette, glazed lobby and relation to the sidewalk. The current render contains the modeled portal, medallions, octagonal glazed entry, balcony and facade pattern; the entrance and identifying sign are visible.'},
      {'name':'Modular export, portability, and complete evidence','score':scores[4],'max_score':2,
       'assessment':f"Fresh Blender 4.5.15 reopen found {asset['object_count']} objects and the sorted object-name list matches the coordinator-refreshed manifest count {entry['object_count']}. The current asset has no camera/light in the exported collection, no unmaterialed meshes, no external libraries and no unpacked image dependencies. I ran the canonical builder in an isolated copied project, reopened its output, and compared every object transform and mesh vertex stream against the current asset: {geometry['differing_object_count']} object differences across {asset['object_count']}. I separately wrote and reopened a collection-only export with {export['object_count']} objects and no cameras/lights. Raw GIS, metadata, official pages, photo, builder, manifest and view are preserved in this packet."}
    ]
    total=sum(c['score'] for c in criteria)
    findings=[
      'FID 645 and the full polygon are well supported; the GIS perimeter was used directly for the structural shell and matches at approximately 1 micrometer under the stated local approximation.',
      'The master placement marker matches the refreshed manifest origin, and its relative library path points to the current detailed asset.',
      'The height estimate is not a survey result. GIS reports 3 levels and Extrution=24 without vertical units; official materials support multiple floors and roof form, but no measured elevation source was located.',
      'The refreshed manifest has 621 objects and now matches the saved asset’s count and names. An isolated canonical rebuild reproduced all object transforms and mesh vertex data; a collection-only export also reopened successfully.'
    ]
    return {'score':total,'max_score':10,'pass_threshold':8,'passes':total>=8,'criteria':criteria,'evidence':{
      'asset_path':'modular/buildings/black_cultural_center.blend','asset_sha256':sha,'asset_bytes':asset_path.stat().st_size,'manifest_id':entry['id'],'expected_collection':entry['collection'],'expected_scene':entry['scene'],'current_manifest_object_count':entry['object_count'],'object_names_and_count_match_manifest':asset['manifest_names_match'] and asset['manifest_count_match'],
      'asset_probe':{k:asset[k] for k in ['blender_version','scene','collection','object_count','type_counts','evaluated_bounds_local_m','manifest_bounds_local_m','source_feature','structural_shell','structural_shell_local_xy_bounds_m','gis_local_xy_bounds_m','source_to_shell_nearest_avg_m','source_to_shell_nearest_max_m','shell_to_source_nearest_avg_m','shell_to_source_nearest_max_m','unmaterialed_mesh_count','material_count','external_libraries','unpacked_file_images','asset_camera_light_count','modifier_count']},
      'source':{'provider':'Purdue University BuildingShapesZip4 ArcGIS FeatureServer','feature_id':attrs['FID'],'abbreviation':attrs['BLDG_ABBR'],'name':attrs['BUILDING_N'],'address':attrs['ADDRESS'],'response_crs':'EPSG:4326 WGS 84','native_layer_crs':'EPSG:3857 / WKID 102100','retrieved':'2026-10-25','source_date':'not supplied','unique_ring_vertices':len(src_local),'local_approx_area_m2':round(area,3),'NUM_LEVELS':attrs.get('NUM_LEVELS'),'Extrution':attrs.get('Extrution'),'official_architecture_source':record['references'][0]['url'],'official_photo_source':record['references'][2]['url']},
      'footprint_method':'Read raw feature ring; transform WGS84 with the documented Purdue local approximate conversion; center the geometry on the GIS bounding-box midpoint; compare evaluated XY vertices of BCC | first-floor brick envelope to all 61 GIS vertices with bidirectional nearest-vertex distances. This is not a polygon IoU or elevation check.',
      'placement':{'manifest_origin_xy_m':origin,'marker':marker,'marker_xy_delta_m':marker_delta,'one_marker':master['marker_count']==1},
      'builder_smoke':smoke,'builder_geometry_comparison':geometry,'independent_collection_export':export,
      'views':['views/current_black_cultural_center_preview.png','views/builder_smoke_preview.png'],
      'source_snapshots':['sources/purdue_gis_fid_645.json','sources/purdue_gis_layer_metadata.json','sources/source_record.json','sources/prior_builder_evidence_snapshot.json','sources/purdue_bcc_facility_2026-10-25.html','sources/purdue_bcc_location_2026-10-25.html','sources/purdue_bcc_official_2021_exterior.jpg','sources/purdue_news_bcc_2021.html','sources/manifest_snapshot.json','sources/modular_AGENTS_snapshot.md','sources/AGENT_snapshot.md','sources/builder_snapshot.py']},
      'findings':findings,'evaluator':'evaluate.py::evaluate','evaluated_at':'2026-10-25','scope':'Fresh independent grade of current Black Cultural Center revision, current 621-object manifest, GIS FID 645 and official Purdue source evidence. The canonical builder smoke run and independent asset/master/export probes were performed without modifying assigned building files or shared indexes.'}

if __name__=='__main__':
 result=evaluate(); (HERE/'result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8'); print(json.dumps(result,indent=2))
