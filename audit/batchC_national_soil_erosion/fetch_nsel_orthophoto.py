"""Fetch the Indiana current orthophoto around NSEL and overlay GIS FID 242."""
import json, math, urllib.parse, urllib.request
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageDraw
from pyproj import Transformer

ROOT=Path(__file__).resolve().parents[2]
AUDIT=Path(__file__).resolve().parent
gis=json.loads((ROOT/'audit/official_building_references.json').read_text(encoding='utf-8'))
feature=next(f for f in gis['buildings'] if int(f.get('fid',-1))==242)
ring=feature['rings_xy_m'][0]
to_ll=Transformer.from_crs(4326,3857,always_xy=True) # replaced below after project inverse
lat0=math.radians(40.4274)
def local_xy_to_lonlat(x,y):
    return (-86.9137+x/(111412.84*math.cos(lat0)),40.4274+y/111040.0)
ll=[local_xy_to_lonlat(x,y) for x,y in ring]
trans=Transformer.from_crs('EPSG:4326','EPSG:3857',always_xy=True)
xy=[trans.transform(lon,lat) for lon,lat in ll]
pad=24.0
bbox=[min(x for x,y in xy)-pad,min(y for x,y in xy)-pad,max(x for x,y in xy)+pad,max(y for x,y in xy)+pad]
w,h=1800,1500
params={'bbox':','.join(f'{v:.3f}' for v in bbox),'bboxSR':'3857','imageSR':'3857','size':f'{w},{h}','format':'jpg','f':'image','interpolation':'RSP_BilinearInterpolation'}
base='https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_Current_Imagery/ImageServer'
url=base+'/exportImage?'+urllib.parse.urlencode(params)
blob=urllib.request.urlopen(url,timeout=60).read()
im=Image.open(BytesIO(blob)).convert('RGB')
raw=AUDIT/'indiana_current_orthophoto_nsel_r1.jpg'
im.save(raw,quality=95)
draw=ImageDraw.Draw(im)
pts=[((x-bbox[0])/(bbox[2]-bbox[0])*w,(bbox[3]-y)/(bbox[3]-bbox[1])*h) for x,y in xy]
draw.line(pts+[pts[0]],fill=(255,40,40),width=5)
cx=sum(x for x,y in pts)/len(pts);cy=sum(y for x,y in pts)/len(pts)
draw.text((cx,cy),'Purdue GIS FID 242 / SOIL',fill=(255,255,0),stroke_width=2,stroke_fill=(0,0,0))
overlay=AUDIT/'indiana_current_orthophoto_nsel_r1_gis_overlay.jpg'
im.save(overlay,quality=95)
identify={'geometry':f'{sum(x for x,y in xy)/len(xy)},{sum(y for x,y in xy)/len(xy)}','geometryType':'esriGeometryPoint','sr':'3857','returnGeometry':'false','returnCatalogItems':'true','f':'json'}
idurl=base+'/identify?'+urllib.parse.urlencode(identify)
catalog=json.loads(urllib.request.urlopen(idurl,timeout=30).read())
meta={'provider':'Indiana Geographic Information Office / Indiana Current Imagery ImageServer','service_url':base,'retrieval_date':'2026-10-24','source_collection':'2022–2025 current imagery; catalog item queried at NSEL centroid','source_crs':'EPSG:3857; project-local footprint inverted through the documented local approximation','project_local_to_lonlat':'lon=-86.9137+x/(111412.84*cos(40.4274deg)); lat=40.4274+y/111040.0','feature_id':242,'feature_name':'Soil Erosion Lab (SOIL)','request_bbox_3857':bbox,'image_px':[w,h],'raw_image':str(raw.relative_to(ROOT)),'overlay_image':str(overlay.relative_to(ROOT)),'identify_catalog_response':catalog,'license':'ImageServer metadata documents CC0 statewide imagery.','limitations':['The project local tangent-plane conversion is approximate and not survey control.','Orthophoto records overhead roof appearance only; it does not establish wall height or roof slope.','Tree shadows and seasonal canopy obscure parts of the perimeter.']}
(AUDIT/'indiana_current_orthophoto_nsel_r1_registration.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'raw_image':str(raw),'image_bytes':len(blob),'bbox_3857':bbox,'catalog':catalog.get('catalogItems',{}).get('features',[])},indent=2))
