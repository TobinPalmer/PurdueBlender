import cv2, json, math
import numpy as np
from pathlib import Path
root=Path('audit/kappa_delta_rho')
img_path=root/'sources/indiana_2023_orthophoto_2026.jpg'
geo=json.loads((root/'sources/purdue_gis_fid801.geojson').read_text(encoding='utf-8-sig'))
ring=geo['features'][0]['geometry']['coordinates'][0]
img=cv2.imread(str(img_path))
h,w=img.shape[:2]
xmin,xmax=-86.91523,-86.91427
ymin,ymax=40.4362,40.4370
def px(lon,lat): return (round((lon-xmin)/(xmax-xmin)*(w-1)), round((ymax-lat)/(ymax-ymin)*(h-1)))
gis=np.array([px(lon,lat) for lon,lat in ring],dtype=np.int32).reshape((-1,1,2))
cv2.polylines(img,[gis],True,(0,40,255),4,cv2.LINE_AA)
# Read structural perimeter from source Blender mesh inspection; no Blender dependency needed here.
probe=json.loads(Path('audit/kappa_delta_rho/source_model_probe.json').read_text())
base=probe['base_ring_xy']
lat0,lon0=40.4274,-86.9137
factor=111412.84*math.cos(math.radians(lat0))
model=[]
for x,y in base:
    lon=lon0+x/factor
    lat=lat0+y/111040.0
    model.append(px(lon,lat))
mdl=np.array(model,dtype=np.int32).reshape((-1,1,2))
cv2.polylines(img,[mdl],True,(255,210,0),3,cv2.LINE_AA)
# crop a generous margin around the GIS envelope
xs=[p[0] for p in gis.reshape(-1,2)]; ys=[p[1] for p in gis.reshape(-1,2)]
pad=90;x0=max(0,min(xs)-pad);x1=min(w,max(xs)+pad);y0=max(0,min(ys)-pad);y1=min(h,max(ys)+pad)
crop=img[y0:y1,x0:x1]
cv2.imwrite(str(root/'gis_orthophoto_overlay.png'),crop)
# save source-only crop without vector lines
source=cv2.imread(str(img_path)); cv2.imwrite(str(root/'sources/indiana_2023_orthophoto_kdr_crop.png'),source[y0:y1,x0:x1])
print(json.dumps({'image':[w,h],'gis_ring_px':gis.reshape(-1,2).tolist(),'model_ring_px':mdl.reshape(-1,2).tolist(),'crop':[x0,y0,x1,y1],'output':str(root/'gis_orthophoto_overlay.png')}))

