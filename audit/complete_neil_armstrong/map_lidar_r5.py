import json,math
from pathlib import Path
import numpy as np
import rasterio
from rasterio.features import geometry_mask
from pyproj import Transformer
from shapely.geometry import Polygon,mapping
from shapely.ops import transform as shp_transform
from PIL import Image,ImageDraw,ImageFont
root=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\complete_neil_armstrong')
# Load exact 3857 GIS ring and reproject to official LiDAR State Plane grid.
gis=json.load(open(root/'sources/gis_feature_642_20261024.json',encoding='utf-8-sig'))
ring=gis['features'][0]['geometry']['rings'][0]; geom=Polygon(ring)
to2968=Transformer.from_crs(3857,2968,always_xy=True)
poly=shp_transform(lambda x,y,z=None:to2968.transform(x,y),geom)
ndds=rasterio.open(root/'sources/tippecanoe_ndhm_clip_r5.tif'); nd=ndds.read(1,masked=True); trans=ndds.transform
mask=geometry_mask([mapping(poly)],out_shape=nd.shape,transform=trans,invert=True,all_touched=False)
vals=nd.compressed()*0.304800609601219
# Read raw data distributions in ft, retain normalized height in m for categories.
summary=json.load(open(root/'lidar_analysis_r5.json',encoding='utf-8'))
summary['vertical_units']='US survey feet in Indiana State Plane/NAVD88 (GEOID12B) per Indiana 2017-2020 QL2 3DEP metadata; NDHM is normalized above-ground height. Converted to meters using 0.304800609601219 m/US survey ft.'
summary['ndhm_raw_percentiles_us_survey_ft']={str(p):float(np.percentile(vals,p)/0.304800609601219) for p in [0,5,10,25,50,75,90,95,99,100]}
summary['ndhm_bins']={}
for low,high in [(0,6),(6,10),(10,14),(14,18),(18,20),(20,22),(22,30),(30,100)]:
  m=mask & (nd.filled(-9999)*0.304800609601219>=low) & (nd.filled(-9999)*0.304800609601219<high)
  summary['ndhm_bins'][f'{low}-{high}m']={'pixels':int(m.sum()),'area_m2':float(m.sum())*trans.a*(-trans.e)*(0.304800609601219**2)}
# Component reports for >=14m, >=18m, >=20m masks (8-connected).
def comps(bmask):
  seen=set(); out=[]; rows,cols=bmask.shape
  for r,c in zip(*np.nonzero(bmask)):
    if (r,c) in seen: continue
    stack=[(int(r),int(c))]; seen.add((int(r),int(c))); pixels=[]
    while stack:
      rr,cc=stack.pop(); pixels.append((rr,cc))
      for dr in (-1,0,1):
       for dc in (-1,0,1):
        nr,nc=rr+dr,cc+dc
        if 0<=nr<rows and 0<=nc<cols and bmask[nr,nc] and (nr,nc) not in seen:
         seen.add((nr,nc)); stack.append((nr,nc))
    if len(pixels)>=8:
      rs=[q[0] for q in pixels]; cs=[q[1] for q in pixels]
      valscomp=np.array([float(nd[rr,cc])*0.304800609601219 for rr,cc in pixels])
      # raster upper-left origin, positive row direction south
      x0=trans.c+min(cs)*trans.a; x1=trans.c+(max(cs)+1)*trans.a
      y1=trans.f-min(rs)*(-trans.e); y0=trans.f-(max(rs)+1)*(-trans.e)
      out.append({'pixels':len(pixels),'area_m2':len(pixels)*trans.a*(-trans.e)*(0.304800609601219**2),'ndhm_median_m':float(np.median(valscomp)),'stateplane_bounds_usft':[x0,y0,x1,y1]})
  out.sort(key=lambda x:x['pixels'],reverse=True)
  return out[:12]
summary['connected_roof_height_zones']={f'ndhm_at_least_{thresh}m':comps(mask & (nd.filled(-9999)*0.304800609601219>=thresh)) for thresh in [14,18,20]}
json.dump(summary,open(root/'lidar_analysis_r5.json','w',encoding='utf-8'),indent=2)
# Build accurately georeferenced raster-cell overlay over the 2023 orthophoto.
base=Image.open(root/'sources/indiana_current_ortho_neil_extent.png').convert('RGBA')
W,H=base.size
bbox=(-9675473.17973648,4928688.31898462,-9675190.20021127,4928833.11569478)
xmin,ymin,xmax,ymax=bbox
to3857=Transformer.from_crs(2968,3857,always_xy=True)
def pix(x,y): return ((x-xmin)/(xmax-xmin)*W,(ymax-y)/(ymax-ymin)*H)
def color(m):
  if m<6:return (35,150,215,170)
  if m<10:return (50,210,165,170)
  if m<14:return (250,225,50,170)
  if m<18:return (255,160,45,170)
  if m<20:return (238,80,30,190)
  if m<22:return (208,35,55,190)
  return (155,35,175,190)
layer=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(layer)
for rr,cc in zip(*np.nonzero(mask & ~np.ma.getmaskarray(nd))):
  m=float(nd[rr,cc])*0.304800609601219
  # Four corners of the 5-ft raster cell into Web Mercator image coordinates.
  corners=[]
  for x,y in [(trans.c+cc*trans.a,trans.f-rr*(-trans.e)),(trans.c+(cc+1)*trans.a,trans.f-rr*(-trans.e)),(trans.c+(cc+1)*trans.a,trans.f-(rr+1)*(-trans.e)),(trans.c+cc*trans.a,trans.f-(rr+1)*(-trans.e))]:
    corners.append(pix(*to3857.transform(x,y)))
  d.polygon(corners,fill=color(m))
base=Image.alpha_composite(base,layer)
d=ImageDraw.Draw(base)
# Official GIS footprint outline.
gispx=[pix(x,y) for x,y in ring]; d.line(gispx+[gispx[0]],fill=(0,105,145,255),width=4)
# Existing source shell walls (red), mapped through the same tangent-plane transform.
wall=json.load(open(root/'sources/shell_wall_edges_r3.json',encoding='utf-8'))
lat0,lon0=40.4274,-86.9137; ox,oy=-109.0,400.1893310546875
def local_to_merc(x,y):
  x+=ox; y+=oy; lat=lat0+y/111040.0; lon=lon0+x/(111412.84*math.cos(math.radians(lat0)))
  return (6378137.0*math.radians(lon),6378137.0*math.log(math.tan(math.pi/4+math.radians(lat)/2)))
for obj in wall:
  pts=[pix(*local_to_merc(v[0],v[1])) for v in obj['vertices']]
  for a,b in obj['edges']:
   p,q=pts[a],pts[b]
   if math.dist(p,q)>.25: d.line((p,q),fill=(220,30,30,255),width=3)
# legend header/footer
page=Image.new('RGBA',(W,H+122),(246,247,249,255)); page.alpha_composite(base,(0,80)); d=ImageDraw.Draw(page)
font=ImageFont.truetype('arial.ttf',25); small=ImageFont.truetype('arial.ttf',16)
d.text((24,12),'Neil Armstrong Hall — 2018 LiDAR normalized height over 2023 aerial',font=font,fill=(23,31,40))
d.text((25,48),'Color cells: 5-ft NDHM height above ground; blue outline: Purdue GIS FID 642; red lines: current modeled wall edges. North up.',font=small,fill=(55,66,76))
legend=[('<6 m',(35,150,215,255)),('6–10 m',(50,210,165,255)),('10–14 m',(250,225,50,255)),('14–18 m',(255,160,45,255)),('18–20 m',(238,80,30,255)),('20–22 m',(208,35,55,255)),('>22 m',(155,35,175,255))]
x=26
for label,col in legend:
 d.rectangle((x,1008,x+18,1026),fill=col); d.text((x+24,1007),label,font=small,fill=(35,45,55)); x+=155
page.convert('RGB').save(root/'lidar_roof_height_r5.png',quality=95)
print(json.dumps({'summary':summary,'image_size':[W,H+122]},indent=2))
