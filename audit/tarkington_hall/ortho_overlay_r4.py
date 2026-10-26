import json, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import Polygon, MultiPoint
from shapely.ops import unary_union

root=Path.cwd(); out=root/'audit'/'tarkington_hall'
feat=json.load(open(out/'gis_feature_662.json',encoding='utf-8'))['feature']
origin=(-591.6124877929688,348.0); lon0=-86.9137; lat0=40.4274
sx=111412.84*math.cos(math.radians(lat0)); sy=111040.0
rings=feat['geometry']['rings']
gisrings=[ [((lon-lon0)*sx-origin[0],(lat-lat0)*sy-origin[1]) for lon,lat in ring] for ring in rings ]
gis=Polygon(gisrings[0],gisrings[1:])
data=json.load(open(out/'shell_vertices_r4.json',encoding='utf-8'))
parts=[MultiPoint(r['vertices_xy']).convex_hull for r in data['objects']]
model=unary_union([p for p in parts if p.geom_type=='Polygon' and p.area>0])
img=Image.open(out/'indiana_2023_ortho_r1.png').convert('RGBA'); w,h=img.size
# Indiana orthophoto request footprint: xmin,ymin,xmax,ymax in EPSG:4326.
bbox=(-86.922,40.429,-86.918,40.433)
def pix(pt):
 x,y=pt; lon=lon0+(x+origin[0])/sx; lat=lat0+(y+origin[1])/sy
 return (round((lon-bbox[0])/(bbox[2]-bbox[0])*w),round((bbox[3]-lat)/(bbox[3]-bbox[1])*h))
overlay=Image.new('RGBA',(w,h),(0,0,0,0)); d=ImageDraw.Draw(overlay,'RGBA')
def fill_poly(poly,fill,outline,width=3):
 pts=[pix(q) for q in poly.exterior.coords]
 d.polygon(pts,fill=fill); d.line(pts,fill=outline,width=width,joint='curve')
 for ring in poly.interiors:
  pts=[pix(q) for q in ring.coords]; d.polygon(pts,fill=(0,0,0,0)); d.line(pts,fill=outline,width=width)
fill_poly(gis,(240,55,65,50),(208,35,55,255),5)
for poly in (model.geoms if hasattr(model,'geoms') else [model]):
 pts=[pix(q) for q in poly.exterior.coords]; d.line(pts,fill=(0,135,255,255),width=5,joint='curve')
img.alpha_composite(overlay)
result=img.convert('RGB')
d=ImageDraw.Draw(result)
try: font=ImageFont.truetype('arial.ttf',28)
except: font=ImageFont.load_default()
d.rectangle((15,15,1050,62),fill=(255,255,255))
d.text((28,25),'Tarkington Hall — 2023 Indiana Orthophoto | red = Purdue GIS FID 662; blue = corrected R4 shell',font=font,fill=(20,30,40))
result.save(out/'ortho_footprint_overlay_r4.png')

