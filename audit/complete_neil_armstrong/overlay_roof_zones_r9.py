import json,math
from pathlib import Path
import numpy as np,rasterio
from rasterio.features import geometry_mask
from pyproj import Transformer
from shapely.geometry import Polygon,mapping
from shapely.ops import transform as tr
from PIL import Image,ImageDraw,ImageFont
root=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\complete_neil_armstrong')
src=root/'sources'
base=Image.open(src/'indiana_current_ortho_neil_extent.png').convert('RGBA');W,H=base.size
bbox=(-9675473.17973648,4928688.31898462,-9675190.20021127,4928833.11569478);xmin,ymin,xmax,ymax=bbox
merc=Transformer.from_crs(2968,3857,always_xy=True)
def pix(x,y):return ((x-xmin)/(xmax-xmin)*W,(ymax-y)/(ymax-ymin)*H)
gis=json.load(open(src/'gis_feature_642_20261024.json',encoding='utf-8-sig'));poly=Polygon(gis['features'][0]['geometry']['rings'][0])
to2968=Transformer.from_crs(3857,2968,always_xy=True);sp=tr(lambda x,y,z=None:to2968.transform(x,y),poly)
with rasterio.open(src/'tippecanoe_ndhm_clip_r5.tif') as ds:
 arr=ds.read(1,masked=True);vals=arr.filled(-9999)*0.304800609601219;valid=~np.ma.getmaskarray(arr)
 mask=geometry_mask([mapping(sp)],out_shape=arr.shape,transform=ds.transform,invert=True,all_touched=False)
 bands=[('14–18m',(25,140,220,155),14,18),('18–20m',(220,40,180,155),18,20),('20–22m',(255,220,40,170),20,22),('>22m',(160,30,190,220),22,100)]
 layer=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(layer)
 for name,col,lo,hi in bands:
  for r,c in zip(*np.nonzero(mask&valid&(vals>=lo)&(vals<hi))):
   corners=[]
   for x,y in [(ds.transform.c+c*ds.transform.a,ds.transform.f+r*ds.transform.e),(ds.transform.c+(c+1)*ds.transform.a,ds.transform.f+r*ds.transform.e),(ds.transform.c+(c+1)*ds.transform.a,ds.transform.f+(r+1)*ds.transform.e),(ds.transform.c+c*ds.transform.a,ds.transform.f+(r+1)*ds.transform.e)]:
    corners.append(pix(*merc.transform(x,y)))
   d.polygon(corners,fill=col)
 out=Image.alpha_composite(base,layer);d=ImageDraw.Draw(out)
 ring=gis['features'][0]['geometry']['rings'][0];pts=[pix(x,y) for x,y in ring];d.line(pts+[pts[0]],fill=(0,95,135,255),width=3)
 out.save(root/'roof_zones_ortho_r9.png')
 print({'image':str(root/'roof_zones_ortho_r9.png'),'bands':[(n,int((mask&valid&(vals>=lo)&(vals<hi)).sum())) for n,c,lo,hi in bands]})
