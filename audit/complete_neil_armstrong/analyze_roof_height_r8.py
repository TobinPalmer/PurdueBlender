import json,hashlib,math
from pathlib import Path
import rasterio,numpy as np
from pyproj import Transformer
from shapely.geometry import Polygon,Point
root=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\complete_neil_armstrong')
src=root/'sources'
gis=json.load(open(src/'gis_feature_642_20261024.json',encoding='utf-8-sig'))
poly=Polygon(gis['features'][0]['geometry']['rings'][0])
to3857=Transformer.from_crs(2968,3857,always_xy=True); to_ll=Transformer.from_crs(3857,4326,always_xy=True)
points=[]
with rasterio.open(src/'tippecanoe_ndhm_clip_r5.tif') as ds:
 arr=ds.read(1,masked=True)
 for r,c in zip(*np.nonzero((arr.filled(-9999)*0.304800609601219)>22)):
  sx,sy=ds.xy(int(r),int(c));mx,my=to3857.transform(sx,sy)
  if not poly.contains(Point(mx,my)):continue
  lon,lat=to_ll.transform(mx,my)
  x=(lon+86.9137)*111412.84*math.cos(math.radians(40.4274))+109.0
  y=(lat-40.4274)*111040.0-400.1893310546875
  points.append({'row':int(r),'col':int(c),'ndhm_m':round(float(arr[r,c])*0.304800609601219,6),'local_xy_m':[round(x,6),round(y,6)]})
out={'source':'2018 Tippecanoe 5-ft NDHM raster, same clipped source used in R5/R7; clipped to official GIS feature FID 642','source_path':'audit/complete_neil_armstrong/sources/tippecanoe_ndhm_clip_r5.tif','gis_source':'audit/complete_neil_armstrong/sources/gis_feature_642_20261024.json','units':'US survey feet converted to meters; local frame inherits R3 registration (X east, Y north, Z up)','threshold_m':22,'high_cell_count_inside_fid_642':len(points),'cells':points,'interpretation':'Only two 5-ft cells within the official footprint exceed 22m; they are localized near X=-13.53m,Y=5.75–7.27m. This does not identify a mechanical penthouse, but it does not support two 22x12m end-located penthouse boxes. FRP independently says a structural-steel mechanical penthouse exists; its exact footprint/form remains unresolved. R8 therefore removes the two unregistered large boxes and louver shells, without claiming the penthouse is absent.'}
json.dump(out,open(root/'roof_height_reconciliation_r8.json','w',encoding='utf-8'),indent=2)
print(json.dumps(out,indent=2))
