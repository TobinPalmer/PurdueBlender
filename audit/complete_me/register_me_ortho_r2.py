"""Download current Indiana orthophoto and overlay both ME GIS footprints."""
from __future__ import annotations
import json, math, urllib.parse, urllib.request
from pathlib import Path
from io import BytesIO
import rasterio
from rasterio.warp import transform
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[2]
AUDIT=Path(__file__).resolve().parent
gis=json.loads((ROOT/'audit/official_building_references.json').read_text(encoding='utf-8'))
features={int(f['fid']):f for f in gis['buildings'] if int(f.get('fid',-1)) in (857,108)}
def local_xy_to_lonlat(x,y):
    return (-86.9137+x/(111412.84*math.cos(math.radians(40.4274))),40.4274+y/111040.0)
def lonlat_to_local(lon,lat):
    return ((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0)
all_ll=[]
for f in features.values(): all_ll.extend([local_xy_to_lonlat(x,y) for x,y in f['rings_xy_m'][0]])
xs,ys=transform('EPSG:4326','EPSG:3857',[p[0] for p in all_ll],[p[1] for p in all_ll])
pad=18.0
bbox=[min(xs)-pad,min(ys)-pad,max(xs)+pad,max(ys)+pad]
w,h=1800,1500
params={'bbox':','.join(f'{v:.3f}' for v in bbox),'bboxSR':'3857','imageSR':'3857','size':f'{w},{h}','format':'jpg','f':'image','interpolation':'RSP_BilinearInterpolation'}
url='https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_Current_Imagery/ImageServer/exportImage?'+urllib.parse.urlencode(params)
img_bytes=urllib.request.urlopen(url,timeout=60).read()
source=Image.open(BytesIO(img_bytes)).convert('RGB')
source.save(AUDIT/'indiana_current_orthophoto_me_r2.jpg',quality=95)
overlay=source.copy();draw=ImageDraw.Draw(overlay)
colors={857:(255,35,35),108:(0,250,255)}
for fid,f in features.items():
    ring=f['rings_xy_m'][0]
    ll=[local_xy_to_lonlat(x,y) for x,y in ring]
    px,py=transform('EPSG:4326','EPSG:3857',[p[0] for p in ll],[p[1] for p in ll])
    points=[((x-bbox[0])/(bbox[2]-bbox[0])*w,(bbox[3]-y)/(bbox[3]-bbox[1])*h) for x,y in zip(px,py)]
    draw.line(points+[points[0]],fill=colors[fid],width=5)
    cx=sum(p[0] for p in points)/len(points);cy=sum(p[1] for p in points)/len(points)
    draw.text((cx,cy),f'FID {fid}',fill=colors[fid],stroke_width=2,stroke_fill=(0,0,0))
overlay.save(AUDIT/'indiana_current_orthophoto_me_r2_gis_overlay.jpg',quality=95)
# Query mosaic catalog item/year at the building centroid.
centers=[]
for fid,f in features.items():
    x,y=f['official_polygon_center_xy_m'];centers.append((fid,*local_xy_to_lonlat(x,y)))
catalog=[]
for fid,lon,lat in centers:
    x,y=transform('EPSG:4326','EPSG:3857',[lon],[lat])
    q={'geometry':f'{x[0]},{y[0]}','geometryType':'esriGeometryPoint','sr':'3857','returnGeometry':'false','returnCatalogItems':'true','f':'json'}
    endpoint='https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_Current_Imagery/ImageServer/identify?'+urllib.parse.urlencode(q)
    catalog.append({'feature_id':fid,'response':json.loads(urllib.request.urlopen(endpoint,timeout=30).read())})
meta={'provider':'Indiana Geographic Information Office / Indiana Current Imagery ImageServer','url':'https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_Current_Imagery/ImageServer','retrieval_date':'2026-10-24','service_metadata':'2022-2025 orthophotography; 4-band 6-inch nominal resolution, CC0','request_bbox_3857':bbox,'image_px':[w,h],'crs':'EPSG:3857 for request/image; campus polygon transformed by documented approximate local-to-lonlat conversion','raw_image':'audit/complete_me/indiana_current_orthophoto_me_r2.jpg','overlay_image':'audit/complete_me/indiana_current_orthophoto_me_r2_gis_overlay.jpg','gis_features':[{'fid':fid,'bounds_local_xy_m':f['aabb_xy_m'],'gis_feature_id':fid,'building_code':f['code']} for fid,f in features.items()],'identify_catalog_responses':catalog,'limitations':['Campus local XY conversion is not survey control; orthophoto/GIS overlay checks general roof-footprint registration only.','Mosaic catalog selection metadata can be missing or generalized; image service reports a 2022-2025 statewide orthophoto collection, so confirm per-image year in the returned catalog fields.','Roof outlines are not wall footprints: eaves, parapets, small pixel shifts and tree cover can affect comparison.']}
(AUDIT/'mechanical_engineering_ortho_registration_r2.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'image_bytes':len(img_bytes),'request_bbox_3857':bbox,'catalog':catalog},indent=2)[:8000])
