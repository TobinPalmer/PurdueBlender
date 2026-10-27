import json,math
from pathlib import Path
from PIL import Image,ImageDraw
root=Path('audit/alpha_epsilon_pi');m=json.loads((root/'fid821_tile_manifest.json').read_text(encoding='utf-8-sig'));z=int(m['z']);tx=int(m['tileX']);ty=int(m['tileY']);im=Image.new('RGB',(768,768))
for y in range(ty-1,ty+2):
 for x in range(tx-1,tx+2): im.paste(Image.open(root/'fid821_tiles'/f'tile_z{z}_y{y}_x{x}.jpg').convert('RGB'),((x-tx+1)*256,(y-ty+1)*256))
def xy(lon,lat):
 n=2**z;return ((lon+180)/360*n*256-(tx-1)*256,(1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*n*256-(ty-1)*256)
d=json.loads((root/'purdue_gis_features_fid754_821.json').read_text(encoding='utf-8-sig'))
f=next(f for f in d['features'] if f['properties']['FID']==821);pts=[xy(*p) for p in f['geometry']['coordinates'][0]]
draw=ImageDraw.Draw(im,'RGBA');draw.line(pts+[pts[0]],fill=(30,255,130,240),width=4);draw.text((12,12),'Official Purdue GIS FID821: Alpha Epsilon Pi / 116 Fowler Ave',fill='white',stroke_width=2,stroke_fill='black');im.save(root/'fid821_satellite_overlay.png')

