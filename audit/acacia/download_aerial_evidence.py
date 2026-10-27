"""Download a small Esri World Imagery tile window around Acacia FID 791."""
import json, math, os, urllib.request
from PIL import Image

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','..'))
AUDIT=os.path.abspath(os.path.dirname(__file__))
SRC=os.path.join(AUDIT,'sources'); os.makedirs(SRC,exist_ok=True)
lat0,lon0=40.4274,-86.9137
house=(40.43060,-86.91752); zoom=20; n=2**zoom
def tile_xy(lat,lon):
    return int((lon+180)/360*n),int((1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*n)
cx,cy=tile_xy(*house); xstart,ystart=cx-1,cy-1
tiles=[]
for ty in range(ystart,ystart+3):
  for tx in range(xstart,xstart+3):
    url=f'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{zoom}/{ty}/{tx}'
    path=os.path.join(SRC,f'esri_world_imagery_z{zoom}_x{tx}_y{ty}.jpg')
    req=urllib.request.Request(url,headers={'User-Agent':'PurdueMapAcaciaEvidence/1.0'})
    with urllib.request.urlopen(req,timeout=40) as resp: data=resp.read()
    with open(path,'wb') as f:f.write(data)
    im=Image.open(path).convert('RGB')
    tiles.append((tx,ty,im,path,url))
mosaic=Image.new('RGB',(3*256,3*256))
for tx,ty,im,path,url in tiles:mosaic.paste(im,((tx-xstart)*256,(ty-ystart)*256))
out=os.path.join(SRC,'esri_world_imagery_acacia_z20_mosaic.jpg'); mosaic.save(out,quality=94)
metadata={'provider':'Esri World Imagery (basemap tile service; local imagery contributors vary)','service_metadata_url':'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer?f=pjson','tile_crs':'Web Mercator Auxiliary Sphere (EPSG:3857)','retrieved':'2026-10-26','zoom':zoom,'center_lat_lon':list(house),'center_tile_xy':[cx,cy],'mosaic':'audit/acacia/sources/esri_world_imagery_acacia_z20_mosaic.jpg','tile_snapshots':[{'url':u,'file':os.path.relpath(p,ROOT)} for _,_,_,p,u in tiles],'imagery_acquisition_date':'not disclosed by the basemap tile endpoint','method':'assembled 3x3 native 256x256 tiles without resampling; tile matrix is north-up','orientation_use':'verify GIS footprint and visible Waldron Street context; facade bearing inference is tied to the street-facing side shown in official Acacia elevation/photo, not inferred from roof color alone','uncertainty':'Imagery date/resolution for this exact tile is not provided by the endpoint; roof/aerial alone cannot establish facade details.'}
with open(os.path.join(SRC,'esri_world_imagery_acacia_metadata.json'),'w',encoding='utf-8') as f:json.dump(metadata,f,indent=2)
print(json.dumps({'center_tile':[cx,cy],'mosaic':out,'tiles':len(tiles)}))
