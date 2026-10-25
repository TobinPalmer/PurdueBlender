import ast,json,math
from pathlib import Path
import cv2,numpy as np
ROOT=Path('.'); out=ROOT/'audit/niswonger_aviation_tech_refine'
# Parse the original 51-point official GIS polygon from the builder, then convert it to asset-local XY.
tree=ast.parse(Path('build_niswonger_aviation_tech.py').read_text(encoding='utf-8'))
pts=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='NISW_PTS' for t in n.targets))
pts=[(x+1325.0,y+1229.5) for x,y in pts]
if pts[0]==pts[-1]:pts=pts[:-1]
def centroid(poly):
 a=0;cx=cy=0
 for (x0,y0),(x1,y1) in zip(poly,poly[1:]+poly[:1]):
  cr=x0*y1-x1*y0;a+=cr;cx+=(x0+x1)*cr;cy+=(y0+y1)*cr
 a*=.5
 return (cx/(6*a),cy/(6*a)),abs(a)
model_c,model_a=centroid(pts)
# OSM footprint way and referenced node coordinates.
obj=json.loads((out/'osm_footprint_way256667242.json').read_text(encoding='utf-8'))
e=obj['elements'];way=next(x for x in e if x['type']=='way');nodes={x['id']:(x['lon'],x['lat']) for x in e if x['type']=='node'}
ll=[nodes[n] for n in way['nodes']]
# Equirectangular local metric coordinates around the OSM polygon mean.
lonc=sum(p[0] for p in ll[:-1])/len(ll[:-1]);latc=sum(p[1] for p in ll[:-1])/len(ll[:-1]);R=6378137.0
osmxy=[(math.radians(lon-lonc)*R*math.cos(math.radians(latc)),math.radians(lat-latc)*R) for lon,lat in ll]
osm_c0,osm_a=centroid(osmxy)
# Use a uniform scale fitted from polygon area. The source GIS polygon and OSM outline differ slightly;
# preserve east/north axes and center them on OSM's exact OSM-way centroid.
scale=math.sqrt(osm_a/model_a)
# tile matrix transform at Esri zoom 20; composite starts tile x=271086,y=395379.
z=20;tile_n=2**z;ox=271086*256;oy=395379*256

def lonlat_to_px(lon,lat):
 x=(lon+180)/360*tile_n*256
 phi=math.radians(lat);y=(1-math.asinh(math.tan(phi))/math.pi)/2*tile_n*256
 return (x-ox,y-oy)
def model_to_px(x,y):
 xm=(x-model_c[0])*scale;ym=(y-model_c[1])*scale
 lon=lonc+math.degrees(xm/(R*math.cos(math.radians(latc))))
 lat=latc+math.degrees(ym/R)
 return lonlat_to_px(lon,lat)
img=cv2.imread(str(out/'arcgis_world_imagery/composite_z20.jpg'))
# OSM outline yellow and official model GIS footprint cyan.
def draw(poly,color,thick):
 ps=np.array([[round(model_to_px(x,y)[0]),round(model_to_px(x,y)[1])] for x,y in poly],dtype=np.int32)
 cv2.polylines(img,[ps],True,color,thick,cv2.LINE_AA)
# Convert OSM points directly from coordinates to tiles.
osm_px=np.array([[round(lonlat_to_px(lon,lat)[0]),round(lonlat_to_px(lon,lat)[1])] for lon,lat in ll],np.int32)
cv2.polylines(img,[osm_px],True,(0,255,255),2,cv2.LINE_AA)
draw(pts,(255,180,0),2)
# R2 roof plates: bounds/XY shapes are the local modeled extents, deliberately labeled as approximate.
for name,x0,x1,y0,y1,color in [('R2 classroom wing',-31.7,4.84,7.15,43.95,(0,0,255)),('R2 brick wing',-39.45,-31.85,7.15,42.35,(255,0,255))]:
 poly=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
 ps=np.array([[round(model_to_px(x,y)[0]),round(model_to_px(x,y)[1])] for x,y in poly],np.int32)
 cv2.polylines(img,[ps],True,color,2,cv2.LINE_AA)
 c=model_to_px((x0+x1)/2,(y0+y1)/2);cv2.putText(img,name,(round(c[0])-50,round(c[1])),cv2.FONT_HERSHEY_SIMPLEX,.4,color,1,cv2.LINE_AA)
cv2.putText(img,'yellow=OSM footprint  cyan=official GIS  red/magenta=approx R2 roof plates',(10,24),cv2.FONT_HERSHEY_SIMPLEX,.48,(255,255,255),2,cv2.LINE_AA)
cv2.imwrite(str(out/'registered_roof_overlay_r3.png'),img)
meta={'source_osm_way':way['id'],'source_osm_timestamp':way['timestamp'],'osm_footprint_latlon_centroid':[lonc,latc],'asset_gis_polygon_area_m2':round(model_a,2),'osm_footprint_area_m2_local':round(osm_a,2),'registration_scale':scale,'registration_method':'Same east/north axes; OSM way centroid center; uniform scale by polygon area to reconcile small source-footprint area difference. This is a qualitative overlay, not a surveyed control fit.','osm_outline_latlon':ll,'official_gis_polygon_local_xy':pts,'roof_plates_local_bounds_xy':{'classroom':[-31.7,4.84,7.15,43.95],'brick':[-39.45,-31.85,7.15,42.35]}}
(out/'orthophoto_registration_r3.json').write_text(json.dumps(meta,indent=2))
print('saved overlay; areas',round(model_a,2),round(osm_a,2),'scale',scale)
