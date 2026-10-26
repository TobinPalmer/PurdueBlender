import json,math
from shapely.geometry import Polygon
from shapely.ops import unary_union
p='audit/massing_hi_vine_dbdf0c5/review/reopen_asset_facts_r1.json'; facts=json.load(open(p)); ring=facts['mesh_objects'][0]['bottom_ring_xy']
# Convert OSM vertices using documented project local transform.
root=__import__('xml.etree.ElementTree',fromlist=['parse'])
r=root.parse('audit/massing_hi_vine_dbdf0c5/sources/osm_map_area_302_vine_2026-10-26.xml').getroot(); nodes={e.get('id'):(float(e.get('lon')),float(e.get('lat'))) for e in r.findall('node')}; way=next(w for w in r.findall('way') if w.get('id')=='860826644'); ll=[nodes[n.get('ref')] for n in way.findall('nd')]
lon0=-86.9137; lat0=40.4274; mx=111412.84*math.cos(math.radians(lat0)); my=111040.0; xy=[((lon-lon0)*mx,(lat-lat0)*my) for lon,lat in ll]
a=Polygon(ring); b=Polygon(xy); inter=a.intersection(b).area; union=a.union(b).area
bounds=a.bounds; obounds=b.bounds
result={'schema':'Hi Vine r1 direct reopen and source overlay validation','asset':facts,'osm_way':'860826644','osm_bounds_local_xy_m':[obounds[0],obounds[1],obounds[2],obounds[3]],'osm_area_m2':b.area,'model_footprint_area_m2':a.area,'footprint_iou_model_to_osm':inter/union,'model_to_osm_hausdorff_m':a.hausdorff_distance(b),'model_bounds_local_xy_m':[bounds[0],bounds[1],bounds[2],bounds[3]],'xy_bbox_delta_m':[bounds[0]-obounds[0],bounds[1]-obounds[1],bounds[2]-obounds[2],bounds[3]-obounds[3]],'checks':{'one_expected_mesh_object':len(facts['mesh_objects'])==1 and facts['mesh_objects'][0]['name']=='Hi Vine','expected_scene_and_collection':facts['scene']=='Building_massing_hi_vine_dbdf0c5' and 'Asset_massing_hi_vine_dbdf0c5' in facts['collections'],'direct_campus_coordinates':facts['mesh_objects'][0]['bounds_world_m'][0][0]>400 and facts['mesh_objects'][0]['bounds_world_m'][1][1]<0,'no_modifiers':not facts['mesh_objects'][0]['modifiers'],'no_external_libraries':not facts['linked_libraries'],'no_external_images':not facts['image_paths'],'flat_top_height_estimated_19_7m':abs(facts['mesh_objects'][0]['bounds_world_m'][2][1]-19.7)<.01}}
json.dump(result,open('audit/massing_hi_vine_dbdf0c5/review/reopen_validation_r1.json','w'),indent=2)
print(json.dumps({k:result[k] for k in ['osm_area_m2','model_footprint_area_m2','footprint_iou_model_to_osm','model_to_osm_hausdorff_m','xy_bbox_delta_m','checks']},indent=2))
