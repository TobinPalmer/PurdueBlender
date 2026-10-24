import json,math
from pathlib import Path
import numpy as np
import rasterio
from rasterio.windows import from_bounds
from rasterio.features import geometry_mask
from rasterio.transform import Affine
from pyproj import Transformer
from shapely.geometry import Polygon,mapping
from shapely.ops import transform as shp_transform
root=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\complete_neil_armstrong')
# Re-query all three public STAC products; preserve their raw item records as provenance snapshots.
records={}
bbox='-86.918,40.427,-86.912,40.433'
import urllib.request, urllib.parse
for product in ['dsm','dtm','ndhm']:
    url=f'https://stac.d2s.org/api/v1/collections/indiana-lidar-{product}/items?'+urllib.parse.urlencode({'bbox':bbox,'limit':100})
    with urllib.request.urlopen(url,timeout=60) as response: j=json.load(response)
    assert len(j['features'])==1,(product,len(j['features']))
    f=j['features'][0]; records[product]=f
    json.dump(j,open(root/f'sources/stac_tippecanoe_{product}_2018_r5.json','w',encoding='utf-8'),indent=2)
# Use the official GIS building ring in its published EPSG:3857 CRS, transformed into the elevation source CRS.
gis=json.load(open(root/'sources/gis_feature_642_20261024.json',encoding='utf-8-sig'))
ring=gis['features'][0]['geometry']['rings'][0]
geom=Polygon(ring)
t=Transformer.from_crs(3857,2968,always_xy=True)
poly=shp_transform(lambda x,y,z=None:t.transform(x,y),geom)
minx,miny,maxx,maxy=poly.bounds
pad=80.0
bounds=(minx-pad,miny-pad,maxx+pad,maxy+pad)
clip_data={}
for product,feat in records.items():
    href=feat['assets']['lidar-image']['href']
    with rasterio.Env(GDAL_HTTP_MULTIRANGE='YES',GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR'):
        with rasterio.open(href) as src:
            win=from_bounds(*bounds,transform=src.transform).round_offsets().round_lengths()
            data=src.read(1,window=win,masked=True)
            trans=src.window_transform(win)
            out=root/f'sources/tippecanoe_{product}_clip_r5.tif'
            profile=src.profile.copy(); profile.update(width=data.shape[1],height=data.shape[0],transform=trans,compress='deflate')
            with rasterio.open(out,'w',**profile) as dst: dst.write(data.filled(src.nodata if src.nodata is not None else -9999).astype('float32'),1)
            clip_data[product]=(data,trans,src.crs,src.res,src.nodata,href)
# common footprint mask within all equal-grid products
nd,transform,crs,res,nodata,href=clip_data['ndhm']
mask=geometry_mask([mapping(poly)],out_shape=nd.shape,transform=transform,invert=True,all_touched=False)
vals=nd.data[mask & ~np.ma.getmaskarray(nd)]
# Elevation summaries for footprint mask and relative height classes.
summary={'gis_mask_pixels':int(mask.sum()),'clip_shape_rows_cols':list(nd.shape),'source_grid_resolution_us_survey_ft':list(res),'source_grid_resolution_m':[float(res[0]*0.304800609601219),float(res[1]*0.304800609601219)],'gis_polygon_state_plane_bounds_usft':[float(v) for v in poly.bounds], 'ndhm_mask_percentiles_m':{str(p):float(np.percentile(vals,p))*0.304800609601219 for p in [0,5,10,25,50,75,90,95,99,100]},'ndhm_pixels_by_height_band':{},'sources':{k:{'stac_item':v['id'],'url':v['assets']['lidar-image']['href'],'date':v['properties'].get('start_datetime','')+' to '+v['properties'].get('end_datetime','')} for k,v in records.items()}}
for low,high in [(0,1),(1,3),(3,6),(6,10),(10,14),(14,20),(20,40),(40,100)]:
    band=mask & (nd.filled(-9999)*0.304800609601219>=low) & (nd.filled(-9999)*0.304800609601219<high)
    summary['ndhm_pixels_by_height_band'][f'{low}-{high}m']={'pixels':int(band.sum()),'area_m2':float(band.sum())*(res[0]*res[1])*(0.304800609601219**2)}
json.dump(summary,open(root/'lidar_analysis_r5.json','w',encoding='utf-8'),indent=2)
print(json.dumps(summary,indent=2))

