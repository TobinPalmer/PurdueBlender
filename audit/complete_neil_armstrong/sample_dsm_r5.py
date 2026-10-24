import json,rasterio
from rasterio.windows import from_bounds
from pyproj import Transformer
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\complete_neil_armstrong\sources\stac_tippecanoe_dsm_2018_r5.json'
j=json.load(open(p,encoding='utf-8-sig')); f=j['features'][0]; url=f['assets']['lidar-image']['href']; crs=f['assets']['lidar-image']['proj:epsg']
# Transform GIS building bounds from geographic coordinates into the DSM's State Plane CRS.
t=Transformer.from_crs(4326,crs,always_xy=True)
lonlat=[(-86.917,-86.913,40.428,40.431)]
xs=[];ys=[]
for lon in [-86.917,-86.913]:
 for lat in [40.428,40.431]:
  x,y=t.transform(lon,lat);xs.append(x);ys.append(y)
print('tile',url,'crs',crs,'bounds',min(xs),min(ys),max(xs),max(ys))
with rasterio.open(url) as ds:
 print('source',ds.width,ds.height,ds.crs,ds.transform,ds.bounds,ds.res,ds.dtypes,ds.nodata)
 win=from_bounds(min(xs),min(ys),max(xs),max(ys),ds.transform).round_offsets().round_lengths()
 print('window',win)
 a=ds.read(1,window=win,masked=True)
 import numpy as np
 vals=a.compressed()
 print('clip',a.shape,'valid',len(vals),'range',float(vals.min()),float(vals.max()),'pcts',np.percentile(vals,[1,5,25,50,75,95,99]).tolist())
