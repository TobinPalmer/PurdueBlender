from pathlib import Path
from PIL import Image, ImageDraw
import json, math, urllib.request
root=Path(__file__).resolve().parents[2]
aud=root/'audit/alpha_tau_omega'
src=aud/'sources'
z=19; n=2**z; cx,cy=135559,197668
# Save a 3x3 Esri World Imagery context mosaic around Purdue GIS FID 785.
mosaic=Image.new('RGB',(768,768),(235,235,235))
for ty in range(cy-1,cy+2):
    for tx in range(cx-1,cx+2):
        tile=src/f'esri_world_imagery_z{z}_{tx}_{ty}.jpg'
        if not tile.exists():
            url=f'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{ty}/{tx}'
            try: urllib.request.urlretrieve(url,tile)
            except Exception: continue
        try:
            im=Image.open(tile).convert('RGB')
            mosaic.paste(im,((tx-(cx-1))*256,(ty-(cy-1))*256))
        except Exception: pass
mosaic.save(src/'esri_world_imagery_fid785_context_z19.jpg',quality=95)

def map_px(lon,lat):
    gx=(lon+180)/360*n*256
    gy=(1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*n*256
    return (gx-(cx-1)*256,gy-(cy-1)*256)
lat0,lon0=40.4274,-86.9137
def xy_ll(x,y): return (lon0+x/(111412.84*math.cos(math.radians(lat0))),lat0+y/111040.0)
def xy_px(x,y): return map_px(*xy_ll(x,y))
d=json.loads((src/'purdue_gis_fid785_2026-10-26.json').read_text(encoding='utf-8-sig'))
feat=d['features'][0]; ring=feat['geometry']['rings'][0]
img=mosaic.convert('RGBA'); dr=ImageDraw.Draw(img,'RGBA')
gispts=[map_px(lon,lat) for lon,lat in ring]
dr.polygon(gispts,fill=(255,25,35,48),outline=(255,35,40,255),width=3)
# Approximate extents of modeled structural wall blocks, in the documented campus XY frame.
parts=[('north/original',(-435.35,-420.15,68.70,83.70)),('south/addition',(-433.455,-420.105,46.00,65.10)),('connector',(-433.455,-420.105,64.25,68.65)),('east kitchen',(-420.0,-413.80,75.175,82.825)),('entry tower',(-436.875,-432.625,64.025,68.475))]
for label,(xmin,xmax,ymin,ymax) in parts:
    pts=[xy_px(xmin,ymin),xy_px(xmax,ymin),xy_px(xmax,ymax),xy_px(xmin,ymax)]
    dr.polygon(pts,fill=(15,105,255,38),outline=(25,100,255,255),width=2)
# Original asset bounds, included only to show what was changed.
old=[(-436.7746,45.8817),(-420.1517,45.8817),(-420.1517,83.8685),(-436.7746,83.8685)]
oldpts=[xy_px(x,y) for x,y in old]; dr.line(oldpts+[oldpts[0]],fill=(255,225,0,255),width=2)
dr.rectangle((6,6,585,70),fill=(0,0,0,205))
dr.text((14,12),'Alpha Tau Omega | Purdue GIS FID 785 | Esri World Imagery z19',fill='white')
dr.text((14,34),'Red: official GIS polygon | blue: modeled structural wall blocks | yellow: old massing bounds',fill=(255,255,180,255))
img.convert('RGB').save(aud/'previews/gis_candidate_footprint_overlay.jpg',quality=95)
