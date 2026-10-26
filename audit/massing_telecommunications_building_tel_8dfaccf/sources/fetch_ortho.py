from pathlib import Path
from urllib.request import urlopen, Request
import json, math
from pyproj import Transformer
root=Path(__file__).resolve().parent
feature=json.loads((root/'purdue_gis_fid199_tel.json').read_text(encoding='utf-8-sig'))['features'][0]
ring=feature['geometry']['rings'][0]
t=Transformer.from_crs(4326,3857,always_xy=True)
pts=[t.transform(p[0],p[1]) for p in ring]
xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
pad=35
bbox=(min(xs)-pad,min(ys)-pad,max(xs)+pad,max(ys)+pad)
url='https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_2018_Imagery/ImageServer/exportImage?bbox='+','.join(f'{v:.3f}' for v in bbox)+'&bboxSR=3857&size=1400,1400&imageSR=3857&format=jpg&f=image'
req=Request(url,headers={'User-Agent':'PurdueBlender building evidence research'})
with urlopen(req,timeout=60) as r: data=r.read(); ctype=r.headers.get('Content-Type','')
(root/'indiana_2018_ortho_tel_bbox.jpg').write_bytes(data)
(root/'ortho_request.json').write_text(json.dumps({'provider':'Indiana Geographic Information Office ArcGIS ImageServer','url':url,'retrieved_date':'2026-10-26','source_date':'2018 imagery','crs':'EPSG:3857','bbox_3857_m':bbox,'image_size':[1400,1400],'content_type':ctype,'measurement_method':'Orthographic roof footprint comparison to Purdue GIS FID 199 transformed from WGS84 to Web Mercator; 35m bbox buffer.','uncertainty':'Overhead imagery only; does not establish roof elevation or facade details.'},indent=2),encoding='utf-8')
print(json.dumps({'image_bytes':len(data),'content_type':ctype,'bbox_3857_m':bbox,'image':str(root/'indiana_2018_ortho_tel_bbox.jpg'),'url':url},indent=2))
