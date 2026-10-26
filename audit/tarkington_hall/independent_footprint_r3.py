"""Independently recompute Tarkington export-only shell/GIS comparison."""
import json, math
from pathlib import Path
from shapely.geometry import Polygon, MultiPoint
from shapely.ops import unary_union

root=Path(__file__).resolve().parents[2]; out=Path(__file__).resolve().parent
feat=json.loads((out/'gis_feature_662.json').read_text(encoding='utf-8'))['feature']
origin=(-591.6124877929688,348.0); lon0=-86.9137; lat0=40.4274
xs=111412.84*math.cos(math.radians(lat0)); ys=111040.0
rings=feat['geometry']['rings']
source=Polygon([((lon-lon0)*xs-origin[0], (lat-lat0)*ys-origin[1]) for lon,lat in rings[0]], [[((lon-lon0)*xs-origin[0],(lat-lat0)*ys-origin[1]) for lon,lat in ring] for ring in rings[1:]])
payload=json.loads((out/'independent_shell_vertices_r3.json').read_text(encoding='utf-8'))
parts=[]
for item in payload['objects']:
    poly=MultiPoint(item['vertices_xy']).convex_hull
    if poly.geom_type=='Polygon' and poly.area>0: parts.append((item['name'],poly))
model=unary_union([p for _,p in parts])
inter=source.intersection(model).area; union=source.union(model).area
def samples(line,step=.25):
    pts=[]
    for part in (line.geoms if hasattr(line,'geoms') else [line]):
        n=max(1,int(math.ceil(part.length/step)))
        pts.extend(part.interpolate(i/n,normalized=True) for i in range(n+1))
    return pts
spts=samples(source.boundary); mpts=samples(model.boundary)
distances=[p.distance(model.boundary) for p in spts]+[p.distance(source.boundary) for p in mpts]
sorted_d=sorted(distances)
report={'building':'Tarkington Hall','revision':'R3 independent','asset':payload['asset'],'sha256':payload['sha256'],'feature_id':feat['attributes']['FID'],'building_code':feat['attributes']['BLDG_ABBR'],'shell_object_count':len(parts),'shell_objects':[n for n,_ in parts],'source_polygon_area_m2':source.area,'model_shell_union_area_m2':model.area,'intersection_area_m2':inter,'union_area_m2':union,'polygon_iou':inter/union,'boundary_sample_step_m':.25,'symmetric_sample_count':len(distances),'symmetric_sampled_boundary_mean_m':sum(distances)/len(distances),'symmetric_sampled_boundary_p95_m':sorted_d[math.floor(.95*(len(sorted_d)-1))],'symmetric_boundary_hausdorff_m':source.boundary.hausdorff_distance(model.boundary),'source_centroid_local_xy_m':[source.centroid.x,source.centroid.y],'model_centroid_local_xy_m':[model.centroid.x,model.centroid.y],'centroid_delta_m':[model.centroid.x-source.centroid.x,model.centroid.y-source.centroid.y],'centroid_delta_length_m':source.centroid.distance(model.centroid),'source_bounds_local_m':[[source.bounds[0],source.bounds[2]],[source.bounds[1],source.bounds[3]]],'model_bounds_local_m':[[model.bounds[0],model.bounds[2]],[model.bounds[1],model.bounds[3]]],'source_crs':'EPSG:4326','local_transform':'X=(lon+86.9137)*111412.84*cos(radians(40.4274)); Y=(lat-40.4274)*111040.0; origin=(-591.6124877929688,348.0)','method':'Reopened canonical .blend in fresh Blender 5.2.3 process, extracted all vertices only from Asset_tarkington_hall shell candidate meshes, transformed by matrix_world, convex-hulled each XY set, and unioned. Metrics recomputed from raw saved Purdue GIS FID 662 snapshot.','limitations':['GIS outline is not documented as surveyed wall faces and may follow roof/eave/cartographic edges.','Project-local geographic conversion is approximate rather than a projected survey CRS.','Convex hull of each selected shell object bridges openings and local setbacks.','This metric excludes non-shell details and does not claim exact wall-to-map alignment.']}
(out/'independent_footprint_r3.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ['shell_object_count','source_polygon_area_m2','model_shell_union_area_m2','polygon_iou','symmetric_sampled_boundary_mean_m','symmetric_sampled_boundary_p95_m','symmetric_boundary_hausdorff_m','centroid_delta_m','centroid_delta_length_m','source_bounds_local_m','model_bounds_local_m']},indent=2))
