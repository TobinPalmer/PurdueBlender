"""Register the NSEL FID242 footprint against 2018 DSM and bare-earth DTM."""
from __future__ import annotations
import json, math, urllib.parse, urllib.request, hashlib
from pathlib import Path
import numpy as np
import rasterio
from rasterio.features import geometry_mask
from rasterio.warp import transform

ROOT=Path(__file__).resolve().parents[2]
AUDIT=Path(__file__).resolve().parent
GIS=json.loads((ROOT/'audit/official_building_references.json').read_text(encoding='utf-8'))
feature=next(f for f in GIS['buildings'] if int(f.get('fid',-1))==242)
DSM=AUDIT/'in2018_29951880_12_dsm.tif'
R=6378137.0
def local_xy_to_lonlat(x,y):
    return (-86.9137+x/(111412.84*math.cos(math.radians(40.4274))),40.4274+y/111040.0)
def esri_transform(x,y):
    q={'geometry':json.dumps({'x':x,'y':y,'spatialReference':{'wkid':4326}},separators=(',',':')),'geometryType':'esriGeometryPoint','sr':'4326','returnGeometry':'false','f':'json'}
    url='https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_2016_2020_DEM/ImageServer/identify?'+urllib.parse.urlencode(q)
    return json.loads(urllib.request.urlopen(url,timeout=30).read())
with rasterio.open(DSM) as ds:
    ring=feature['rings_xy_m'][0]
    ll=[local_xy_to_lonlat(x,y) for x,y in ring]
    px,py=transform('EPSG:4326',ds.crs,[p[0] for p in ll],[p[1] for p in ll])
    polygon={'type':'Polygon','coordinates':[list(zip(px,py))+[(px[0],py[0])]]}
    arr=ds.read(1)
    mask=geometry_mask([polygon],out_shape=arr.shape,transform=ds.transform,invert=True,all_touched=False)
    vals=arr[mask&np.isfinite(arr)&(arr>0)]
    xs=[p[0] for p in ring];ys=[p[1] for p in ring]
    grid=[]
    for iy in range(5):
      for ix in range(5):
        x=min(xs)+(ix+.5)*(max(xs)-min(xs))/5
        y=min(ys)+(iy+.5)*(max(ys)-min(ys))/5
        lon,lat=local_xy_to_lonlat(x,y)
        qx,qy=transform('EPSG:4326',ds.crs,[lon],[lat])
        row,col=ds.index(qx[0],qy[0])
        if not (0<=row<ds.height and 0<=col<ds.width) or not (mask[row,col]): continue
        r0,r1=max(0,row-2),min(ds.height,row+3);c0,c1=max(0,col-2),min(ds.width,col+3)
        sub=arr[r0:r1,c0:c1];msk=mask[r0:r1,c0:c1]&np.isfinite(sub)&(sub>0)
        if not np.any(msk):continue
        dsm=float(np.median(sub[msk]))
        terrain=esri_transform(lon,lat)
        ground=float(terrain['value'])
        grid.append({'grid_xy':[ix+1,iy+1],'local_xy_m':[round(x,3),round(y,3)],'lonlat':[lon,lat],'dsm_neighborhood_median_ftUS':dsm,'dtm_bare_earth_ftUS':ground,'dsm_minus_dtm_ft':dsm-ground,'dtm_source_status':terrain.get('status'),'dtm_catalog_items':terrain.get('catalogItems',{})})
    if not vals.size: raise RuntimeError('No DSM cell centers intersect the registered FID242 footprint')
    results={'source':{'provider':'Indiana Geographic Information Office / 2018 3DEP QL2 DSM','url':'https://giselevationingov.s3.us-east-2.amazonaws.com/dsmoptimized/statewide/2018/SPW/5ft/in2018_29951880_12_dsm.tif','retrieval_date':'2026-10-24','acquisition_date':'2018-04-20 per Indiana Statewide 3DEP Lidar Dates MapServer layer 4, Field4 (epoch ms 1524182400000)','acquisition_date_source':'https://gisdata.in.gov/server/rest/services/Indiana_Statewide_3DEP_Lidar_Dates/MapServer/4','crs':ds.crs.to_string(),'pixel_size_native_ft':[abs(float(ds.transform.a)),abs(float(ds.transform.e))],'tile_sha256':hashlib.sha256(DSM.read_bytes()).hexdigest(),'license':'CC0'},'footprint_source':{'provider':'Purdue campus GIS','url':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0','feature_id':242,'name':'Soil Erosion Lab','snapshot':'audit/batchC_national_soil_erosion_official_footprint.json','local_xy_conversion':'lon=-86.9137+x/(111412.84*cos(40.4274deg)); lat=40.4274+y/111040','uncertainty':'Project-local tangent plane is approximate, not survey control.'},'fid242_dsm':{'cell_count':int(vals.size),'elevation_ftUS_quantiles_p10_p25_p50_p75_p90_p95_p99_max':[float(x) for x in np.percentile(vals,[10,25,50,75,90,95,99,100])],'dominant_1ft_bin':None if not vals.size else [float(np.floor(np.median(vals))),float(np.floor(np.median(vals))+1)],'grid_samples':grid,'interpretation':'DSM raster records the uppermost surface, including roof, equipment, vegetation, and artifacts. Median local neighborhoods were compared to same-coordinate bare-earth DTM queries; this is an estimated above-ground surface, not surveyed wall height.'},'limitations':['5-ft DSM cells are coarse relative to individual rooftop elements.','DTM identify samples on the building are interpolated terrain, not directly observed beneath the structure.','NSEL roof is broad and visually mostly white in the 2023 orthophoto, but rooftop equipment and shadows can alter local DSM samples.','Tile-specific acquisition timestamp is documented by the Indiana 3DEP tile-date service (2018-04-20); this is a historic surface snapshot and may not match later renovations.']}
out=AUDIT/'nsel_lidar_height_r1.json'
out.write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'source':results['source'],'footprint':results['footprint_source'],'dsm':{k:v for k,v in results['fid242_dsm'].items() if k!='grid_samples'},'grid':[{k:v for k,v in p.items() if k!='dtm_catalog_items'} for p in grid]},indent=2))
