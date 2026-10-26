import json, math, hashlib
from pathlib import Path
from shapely.geometry import Polygon, Point
from shapely.ops import transform
from pyproj import Transformer
folder=Path(__file__).resolve().parent
expected='795eef2993264674747768df2bd29ff6bdef3ff7ab48d33299c03060691b67d6'
model_path=folder.parents[1]/'modular'/'buildings'/'zeta_tau_alpha.blend'
sha=hashlib.sha256(model_path.read_bytes()).hexdigest()
assert sha==expected, f'Candidate SHA changed: {sha}'
raw=json.loads((folder/'gis_fid773_raw.json').read_text(encoding='utf-8'))['feature']
ring=raw['geometry']['rings'][0]
R=6378137.0
coords=[]
for x,y in ring:
    lon=math.degrees(x/R)
    lat=math.degrees(2*math.atan(math.exp(y/R))-math.pi/2)
    X=(lon+86.9137)*111412.84*math.cos(math.radians(40.4274))
    Y=(lat-40.4274)*111040.0
    coords.append((X,Y))
source_world=Polygon(coords)
cent=source_world.centroid
source=Polygon([(x-cent.x,y-cent.y) for x,y in coords])
extract=json.loads((folder/'independent_grade_r1_extract.json').read_text(encoding='utf-8'))
model=Polygon(extract['shell_base_ring_xy_ordered'])
assert source.is_valid and model.is_valid
intersection=source.intersection(model).area
union=source.union(model).area
# symmetric distances sampled at half metre intervals

def samples(poly, step=.5):
    b=poly.boundary
    n=max(1,math.ceil(b.length/step))
    return [b.interpolate(b.length*i/n) for i in range(n)]
def directed(a,b): return [b.distance(p) for p in samples(a)]
dists=directed(source,model.boundary)+directed(model,source.boundary)
dists.sort()
metrics={
 'candidate_sha256':sha,'source_fid':raw['attributes']['FID'],'source_name':raw['attributes']['BUILDING_N'],'source_address':raw['attributes']['ADDRESS'],
 'source_crs':'EPSG:3857 (metadata latestWkid 3857)','model_ring_vertices':len(extract['shell_base_ring_xy_ordered']),
 'source_ring_vertices':len(coords)-1,'source_polygon_area_m2':source.area,'model_shell_base_area_m2':model.area,
 'intersection_area_m2':intersection,'union_area_m2':union,'footprint_iou':intersection/union,
 'source_bounds_local_m':source.bounds,'model_bounds_local_m':model.bounds,
 'source_centroid_local_m':list(source.centroid.coords[0]),'model_centroid_local_m':list(model.centroid.coords[0]),
 'centroid_error_m':source.centroid.distance(model.centroid),
 'symmetric_boundary_mean_m':sum(dists)/len(dists),'symmetric_boundary_p95_m':dists[math.ceil(.95*len(dists))-1],
 'symmetric_boundary_hausdorff_m':source.boundary.hausdorff_distance(model.boundary),
 'model_geometry_evidence':'base perimeter cycle reconstructed from the saved shell mesh bottom edges, not copied from builder report',
 'source_geometry_evidence':'raw saved ArcGIS FID 773 ring independently inverse-Web-Mercator projected and transformed to repository local meter approximation',
 'source_attributes':{k:raw['attributes'].get(k) for k in ['BLDG_ABBR','BUILDING_N','ADDRESS','NUM_LEVELS','CountOfFLO','Extrution','Shape__Area','Shape__Length']}
}
out=folder/'independent_grade_r1_metrics.json'
out.write_text(json.dumps(metrics,indent=2),encoding='utf-8')
print(json.dumps(metrics,indent=2))
