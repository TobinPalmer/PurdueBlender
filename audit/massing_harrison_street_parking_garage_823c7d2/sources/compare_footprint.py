import json, math
from pathlib import Path
from shapely.geometry import Polygon
root=Path.cwd(); base=root/'audit/massing_harrison_street_parking_garage_823c7d2/sources'
j=json.loads((base/'purdue_gis_FID892.json').read_text(encoding='utf-8-sig'))['feature']
ring=j['geometry']['rings'][0]
xy=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0) for lon,lat in ring]
if xy[0]==xy[-1]: xy=xy[:-1]
gis=Polygon(xy)
pre=json.loads((base/'prebuild_footprint_vertices.json').read_text())['bottom_vertices_world_m']
old=Polygon([(p[0],p[1]) for p in pre])
print(json.dumps({'gis_vertices':len(ring),'gis_area_m2':gis.area,'gis_bounds':gis.bounds,'old_vertices':len(pre),'old_area_m2':old.area,'old_bounds':old.bounds,'intersection_area':gis.intersection(old).area,'iou':gis.intersection(old).area/gis.union(old).area,'gis_to_old_hausdorff_m':gis.hausdorff_distance(old),'gis_centroid':list(gis.centroid.coords)[0],'old_centroid':list(old.centroid.coords)[0]},indent=2))
