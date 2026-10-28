"""Compare OSM and Indiana 2018 footprints in the project approximate XY frame."""
import json, math, os
from shapely.geometry import Polygon
here=os.path.dirname(os.path.abspath(__file__))
osm=json.load(open(os.path.join(here,'source_osm_way_860918859_raw.json'),encoding='utf-8'))
state=json.load(open(os.path.join(here,'source_indiana_building_footprint_2018_objectid_409445_raw.json'),encoding='utf-8'))
onodes=osm['nodes'][:-1]
oring=[(n['lon'],n['lat']) for n in onodes]
sring=state['features'][0]['geometry']['rings'][0][:-1]
lat0,lon0=40.4274,-86.9137
def project(p):
    lon,lat=p
    return ((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0)
def poly_area(points):
    p=[project(q) for q in points]
    return abs(sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p)))/2)
def bounds(points):
    p=[project(q) for q in points]
    return {'x':[min(q[0] for q in p),max(q[0] for q in p)],'y':[min(q[1] for q in p),max(q[1] for q in p)]}
op=[project(q) for q in oring]; sp=[project(q) for q in sring]
opoly=Polygon(op); spoly=Polygon(sp)
nearest_osm=[min(math.dist(p,q) for q in sp) for p in op]
nearest_state=[min(math.dist(p,q) for q in op) for p in sp]
result={
 'retrieval_date':'2026-10-27',
 'method':'Project each WGS84 vertex using the documented local approximation; calculate shoelace area and symmetric nearest-vertex distances. This compares mapped outlines, not structural wall faces or survey control.',
 'project_transform':{'origin_latitude':lat0,'origin_longitude':lon0,'x_formula':'(longitude + 86.9137) * 111412.84 * cos(radians(40.4274))','y_formula':'(latitude - 40.4274) * 111040.0','units':'meters; approximate local conversion, not surveyed CRS'},
 'osm':{'feature':'way/860918859','vertex_count':len(op),'area_m2':poly_area(oring),'bounds_m':bounds(oring),'vertices_projected_xy':op},
 'indiana_state_footprint':{'feature_layer':'Indiana Building Footprints 2016-2020','objectid':state['features'][0]['attributes']['objectid'],'lidaryear':state['features'][0]['attributes']['lidaryear'],'vertex_count':len(sp),'reported_shape_area_field':state['features'][0]['attributes'].get('SHAPE__Area'),'area_from_returned_geometry_m2':poly_area(sring),'bounds_m':bounds(sring),'vertices_projected_xy':sp},
 'symmetric_nearest_vertex_distances_m':{'osm_to_state':[round(x,4) for x in nearest_osm],'max_osm_to_state':max(nearest_osm),'mean_osm_to_state':sum(nearest_osm)/len(nearest_osm),'state_to_osm':[round(x,4) for x in nearest_state],'max_state_to_osm':max(nearest_state),'mean_state_to_osm':sum(nearest_state)/len(nearest_state)},
 'polygon_overlay':{'intersection_area_m2':opoly.intersection(spoly).area,'union_area_m2':opoly.union(spoly).area,'intersection_over_union':opoly.intersection(spoly).area/opoly.union(spoly).area,'symmetric_difference_area_m2':opoly.symmetric_difference(spoly).area,'boundary_hausdorff_distance_m':opoly.boundary.hausdorff_distance(spoly.boundary)},
 'interpretation':'The state lidar-derived outline is slightly larger and near-coincident with the named OSM church outline. This is consistent with an outer roof/eave envelope around a core wall outline, but the dataset does not label roof edges and no survey plan verifies that interpretation. Keep the existing OSM wall base and model the roof overhang explicitly; do not treat the two polygons as identical ground-truth wall footprints.'
}
json.dump(result,open(os.path.join(here,'footprint_comparison_2026-10-27.json'),'w',encoding='utf-8'),indent=2)
print(json.dumps(result,indent=2))
