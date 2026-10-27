import json, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
root=Path('audit/alpha_epsilon_pi')
manifest=json.loads((root/'imagery_tile_manifest.json').read_text(encoding='utf-8-sig'))
z=manifest['z']; n=2**z; xmin=int(manifest['xmin']); ymin=int(manifest['ymin'])
canvas=Image.new('RGB',((int(manifest['xmax'])-xmin+1)*256,(int(manifest['ymax'])-ymin+1)*256))
for y in range(ymin,int(manifest['ymax'])+1):
    for x in range(xmin,int(manifest['xmax'])+1):
        p=root/'tiles'/f'tile_z{z}_y{y}_x{x}.jpg'
        canvas.paste(Image.open(p).convert('RGB'),((x-xmin)*256,(y-ymin)*256))
def xy(lon,lat):
    px=(lon+180)/360*n*256; r=math.radians(lat); py=(1-math.asinh(math.tan(r))/math.pi)/2*n*256
    return px-xmin*256,py-ymin*256
features=json.loads((root/'purdue_gis_features_fid754_821.json').read_text(encoding='utf-8-sig'))['features']
d=ImageDraw.Draw(canvas,'RGBA')
for f,color in [(f,(20,120,255,220) if f['properties']['FID']==754 else (60,240,120,220)) for f in features]:
    ring=f['geometry']['coordinates'][0]
    pts=[xy(lon,lat) for lon,lat in ring]
    d.line(pts+[pts[0]],fill=color,width=4)
    cx=sum(p[0] for p in pts)/len(pts); cy=sum(p[1] for p in pts)/len(pts)
    label=f"FID {f['properties']['FID']} GIS: {f['properties']['BUILDING_N']}"
    d.rectangle((cx-4,cy-4,cx+4,cy+4),fill=color)
    d.text((cx+6,cy+4),label,fill=(255,255,255,255),stroke_width=2,stroke_fill=(0,0,0,255))
for p,color,label in [(manifest['points'][0],(255,180,0,255),'FID754 centroid'),(manifest['points'][1],(255,40,40,255),'OSM geocode 1051 David Ross Rd')]:
    px,py=xy(p['lon'],p['lat']); d.ellipse((px-7,py-7,px+7,py+7),fill=color,outline=(0,0,0,255),width=2); d.text((px+8,py-15),label,fill=(255,255,255,255),stroke_width=2,stroke_fill=(0,0,0,255))
canvas.save(root/'satellite_footprint_overlay.png')
print(canvas.size, root/'satellite_footprint_overlay.png')
