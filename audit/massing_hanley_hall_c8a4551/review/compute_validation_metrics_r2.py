import json,math
from pathlib import Path
from shapely.geometry import Polygon
from shapely.validation import explain_validity
ROOT=Path.cwd(); A=ROOT/'audit/massing_hanley_hall_c8a4551'; REVIEW=A/'review'
ins=json.loads((REVIEW/'reopen_mesh_inspection_r2.json').read_text())
def xy(lon,lat): return ((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0)
raw=json.loads((A/'sources/purdue_campus_gis_hanley.json').read_text(encoding='utf-8-sig'))
gf=next(f for f in raw['features'] if f['attributes'].get('OBJECTID')==310)
gis_pts=[xy(*p) for p in gf['geometry']['rings'][0]]
if gis_pts[0]==gis_pts[-1]: gis_pts.pop()
osmraw=json.loads((A/'sources/osm_way_283275000_raw.json').read_text()); nm={n['id']:n for n in osmraw['nodes']}
osm_pts=[xy(nm[i]['lon'],nm[i]['lat']) for i in osmraw['way']['nodes']]
if osm_pts[0]==osm_pts[-1]: osm_pts.pop()
base=ins['base_ring_xy_m']; eave=ins['eave_xy_candidates_m']
# Map every authoritative point to the closest corresponding mesh vertex; retain source order.
mesh_gis=[min(base,key=lambda q:math.dist(q,p)) for p in gis_pts]
mesh_osm=[min(eave,key=lambda q:math.dist(q,p)) for p in osm_pts]
p_gis=Polygon(gis_pts); p_osm=Polygon(osm_pts); p_mesh_gis=Polygon(mesh_gis); p_mesh_osm=Polygon(mesh_osm)
wall_err=max(math.dist(x,y) for x,y in zip(mesh_gis,gis_pts))
roof_err=max(math.dist(x,y) for x,y in zip(mesh_osm,osm_pts))
areaft=34064.0; floorarea=areaft*.09290304
res={
 'asset':'modular/buildings/massing_hanley_hall_c8a4551.blend','asset_reopened_directly':True,
 'scene':ins['scene'],'collection':ins['collection'],'export_objects':ins['collection_object_names'],
 'object_count':ins['object_count'],'mesh_vertices':ins['mesh_vertices'],'mesh_faces':ins['mesh_faces'],
 'world_bounds_xyz_m':ins['bounds_world_xyz_m'],'mesh_modifiers':ins['modifiers'],'linked_libraries':ins['linked_libraries'],'unpacked_external_images':ins['unpacked_external_images'],
 'wall_footprint':{'source':'Purdue Campus GIS OBJECTID 310 / HNLY','source_vertices':len(gis_pts),'source_area_m2':p_gis.area,'source_bounds_xy_m':list(p_gis.bounds),'mesh_matched_vertices':len(mesh_gis),'max_source_to_mesh_vertex_error_m':wall_err,'source_validity':explain_validity(p_gis),'mesh_ring_validity':explain_validity(p_mesh_gis),'mesh_ring_area_m2':p_mesh_gis.area,'mesh_to_source_iou':p_mesh_gis.intersection(p_gis).area/p_mesh_gis.union(p_gis).area},
 'roof_eave_outline':{'source':'OSM way 283275000 / Hanley Hall; visually supported as outer roof/eave ring by Indiana current aerial','source_vertices':len(osm_pts),'source_area_m2':p_osm.area,'source_bounds_xy_m':list(p_osm.bounds),'mesh_matched_vertices':len(mesh_osm),'max_source_to_mesh_vertex_error_m':roof_err,'source_validity':explain_validity(p_osm),'mesh_ring_validity':explain_validity(p_mesh_osm),'mesh_ring_area_m2':p_mesh_osm.area,'mesh_to_source_iou':p_mesh_osm.intersection(p_osm).area/p_mesh_osm.union(p_osm).area},
 'source_difference_and_resolution':{'area_delta_m2':p_osm.area-p_gis.area,'area_ratio_osm_to_gis':p_osm.area/p_gis.area,'wall_to_eave_iou':p_gis.intersection(p_osm).area/p_gis.union(p_osm).area,'centroid_offset_m':p_gis.centroid.distance(p_osm.centroid),'boundary_hausdorff_m':p_gis.hausdorff_distance(p_osm),'orthophoto_interpretation':'Current orthophoto overlay shows the smaller official GIS wall ring inset inside the larger OSM edge along the visible roof perimeter; the builder now models these as wall and eave respectively.'},
 'vertical_evidence':{'official_floors':3,'source':'Purdue OEP emergency plan revision 2026-03-31','estimated_wall_eave_height_m':14.8,'estimated_ridge_height_m':16.08,'actual_mesh_z_min_m':ins['bounds_world_xyz_m'][2][0],'actual_mesh_z_max_m':ins['bounds_world_xyz_m'][2][1],'height_status':'Estimated; no measured building elevation/section.'},
 'area_plausibility_check':{'official_campus_gis_squarefootage_attribute_sqft':areaft,'approx_gross_m2':floorarea,'three_floor_mean_gross_per_floor_m2':floorarea/3,'GIS_wall_footprint_x3_sqft':p_gis.area*3/0.09290304,'OSM_eave_footprint_x3_sqft':p_osm.area*3/0.09290304,'assessment':'This is a plausibility check only; published square footage basis and void/atrium treatment are unspecified.'},
 'entrance':'Single glazed entrance bay modeled on the probable playground-facing/north side from photo + aerial context. Side selection remains inferred; no georeferenced entrance drawing found.',
 'renders':['audit/massing_hanley_hall_c8a4551/renders/hanley_hall_facade.png','audit/massing_hanley_hall_c8a4551/renders/hanley_entry_review.png'],
 'validation_result':'pass' if wall_err<.001 and roof_err<.001 and ins['object_count']==1 and not ins['modifiers'] and not ins['linked_libraries'] and not ins['unpacked_external_images'] else 'fail'
}
(REVIEW/'reopen_validation_r2.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps({k:v for k,v in res.items() if k not in ('wall_footprint','roof_eave_outline','source_difference_and_resolution','area_plausibility_check')},indent=2))
print(json.dumps({'wall':res['wall_footprint'],'roof':res['roof_eave_outline'],'sources':res['source_difference_and_resolution']},indent=2))
