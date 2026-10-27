"""Download current Esri World Imagery tiles around Purdue GIS FID 431."""
import json, math, os, urllib.request
from PIL import Image
from pathlib import Path
AUDIT=Path(__file__).resolve().parent
SRC=AUDIT/'sources'; SRC.mkdir(parents=True,exist_ok=True)
lat,lon=40.42805,-86.92420
zoom=20; n=2**zoom
def tile_xy(lat,lon):
 return int((lon+180)/360*n),int((1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*n)
cx,cy=tile_xy(lat,lon); xstart,ystart=cx-1,cy-1; tiles=[]
for ty in range(ystart,ystart+3):
 for tx in range(xstart,xstart+3):
  url=f'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{zoom}/{ty}/{tx}'
  path=SRC/f'esri_world_imagery_z{zoom}_x{tx}_y{ty}.jpg'
  req=urllib.request.Request(url,headers={'User-Agent':'PurdueMapHullEvidence/1.0'})
  with urllib.request.urlopen(req,timeout=40) as r: path.write_bytes(r.read())
  im=Image.open(path).convert('RGB'); tiles.append((tx,ty,im,str(path),url))
mosaic=Image.new('RGB',(3*256,3*256))
for tx,ty,im,_,_ in tiles:mosaic.paste(im,((tx-xstart)*256,(ty-ystart)*256))
out=SRC/'esri_world_imagery_fid431_z20_mosaic.jpg'; mosaic.save(out,quality=95)
meta={'provider':'Esri World Imagery (basemap tile service; local imagery contributors vary)','service_metadata_url':'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer?f=pjson','tile_crs':'Web Mercator Auxiliary Sphere (EPSG:3857)','retrieved':'2026-10-26','zoom':zoom,'center_lat_lon':[lat,lon],'center_tile_xy':[cx,cy],'mosaic':str(out.relative_to(AUDIT.parents[1])),'tile_snapshots':[{'url':u,'file':str(Path(p).relative_to(AUDIT.parents[1]))} for _,_,_,p,u in tiles],'imagery_acquisition_date':'not disclosed by basemap tile endpoint','method':'assembled 3x3 native 256x256 tiles without resampling; north-up','limitations':'Satellite imagery supports plan and roof context, not facade orientation details or height; the FID 431 GIS polygon is the footprint source.'}
(SRC/'esri_imagery_metadata.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'center_tile':[cx,cy],'mosaic':str(out),'tiles':len(tiles)},indent=2))
