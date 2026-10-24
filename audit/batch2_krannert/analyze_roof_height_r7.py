from __future__ import annotations
import json, math, urllib.parse, urllib.request, hashlib, sys
from pathlib import Path
SCRIPT_DIR=Path(__file__).resolve().parent
sys.path=[p for p in sys.path if Path(p or '.').resolve()!=SCRIPT_DIR]
import numpy as np
import rasterio
from rasterio.features import geometry_mask
from rasterio.warp import transform
ROOT=Path(__file__).resolve().parents[2]
AUDIT=SCRIPT_DIR
DSM=ROOT/'audit/complete_knoy/indiana_3dep_2018_dsm_in2018_30001885_12.tif'
GIS=ROOT/'audit/batch2_krannert/krannert_gis_fid54_4326.json'
OUT=AUDIT/'roof_height_assessment_r7.json'
raw=json.loads(GIS.read_text(encoding='utf-8'))
feature=raw['features'][0]
ring=feature['geometry']['rings'][0]
lonlat=[(float(p[0]),float(p[1])) for p in ring]
# Exact boundary from Purdue GIS feature; no model/manual fit.
with rasterio.open(DSM) as ds:
    xs,ys=transform('EPSG:4326',ds.crs,[p[0] for p in lonlat],[p[1] for p in lonlat])
    coords=list(zip(xs,ys))
    geom={'type':'Polygon','coordinates':[coords+[coords[0]]]}
    arr=ds.read(1)
    mask=geometry_mask([geom],out_shape=arr.shape,transform=ds.transform,invert=True,all_touched=False)
    vals=arr[mask & np.isfinite(arr) & (arr>0)].astype('float64')
    dsm_info={'crs':ds.crs.to_string(),'transform':[float(v) for v in ds.transform[:6]],'shape_px':[int(ds.height),int(ds.width)],'pixel_size': [abs(float(ds.transform.a)),abs(float(ds.transform.e))],'nodata':ds.nodata,'valid_cell_centers':int(len(vals)),'quantiles_ftUS':{f'p{q}':float(np.percentile(vals,q)) for q in [0,10,25,50,75,90,95,99,100]}}
# Ray cast in WGS84 to select interior DEM query points without interpreting the
# undocumented local GIS height fields as ground elevations.
def inside(lon,lat):
    hit=False
    for i,(x1,y1) in enumerate(lonlat):
        x2,y2=lonlat[(i+1)%len(lonlat)]
        if (y1>lat)!=(y2>lat) and lon < (x2-x1)*(lat-y1)/(y2-y1)+x1:
            hit=not hit
    return hit
minlon,maxlon=min(x for x,y in lonlat),max(x for x,y in lonlat)
minlat,maxlat=min(y for x,y in lonlat),max(y for x,y in lonlat)
samples=[]
for iy in range(1,7):
    for ix in range(1,7):
        lon=minlon+(maxlon-minlon)*ix/7
        lat=minlat+(maxlat-minlat)*iy/7
        if not inside(lon,lat): continue
        geompt=json.dumps({'x':lon,'y':lat,'spatialReference':{'wkid':4326}},separators=(',',':'))
        q=urllib.parse.urlencode({'geometry':geompt,'geometryType':'esriGeometryPoint','sr':'4326','returnGeometry':'false','f':'json'})
        url='https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_2016_2020_DEM/ImageServer/identify?'+q
        with urllib.request.urlopen(url,timeout=30) as response: result=json.load(response)
        try: value=float(result['value'])
        except (KeyError,TypeError,ValueError): continue
        samples.append({'longitude':lon,'latitude':lat,'bare_earth_elevation_ft':value})
terrain=np.array([x['bare_earth_elevation_ft'] for x in samples],dtype='float64')
if len(vals)==0 or len(terrain)==0: raise RuntimeError(f'No valid samples DSM={len(vals)}, DTM={len(terrain)}')
ground_med=float(np.median(terrain)); dsm_med=float(np.median(vals)); agl=dsm_med-ground_med
quant_agl={f'p{q}':float(np.percentile(vals,q)-ground_med) for q in [10,25,50,75,90,95,99,100]}
model={'ground':0.0,'L1':12.7,'L2':28.0,'L3':40.7,'L4':53.5,'L5':66.2,'L6':78.9,'L7':91.6,'roof_deck':104.3,'parapet_top':108.0,'penthouse_top':117.0,'elevator_overrun_top':120.7}
report={
 'building_id':'krannert_building','revision':7,'review_date':'2026-10-24',
 'assessment':'Independent approximate LiDAR/DEM roof-surface check. No model height or geometry changed.',
 'dsm_source':{'provider':'Indiana Geographic Information Office / Indiana Statewide Elevation Catalog','title':'Indiana 2016-2020 QL2 3DEP LiDAR, 2018 Tippecanoe tile','tile':'in2018_30001885_12','acquisition_date':'2018-04-20','download_url':'https://giselevationingov.s3.us-east-2.amazonaws.com/dsmoptimized/statewide/2018/SPW/5ft/in2018_30001885_12.tif','local_file':'audit/complete_knoy/indiana_3dep_2018_dsm_in2018_30001885_12.tif','sha256':hashlib.sha256(DSM.read_bytes()).hexdigest(),'product':'DSM, 5 ft cells, elevations in US survey feet; NAD83(HARN) / Indiana West (ftUS)','license':'CC0'},
 'terrain_source':{'provider':'Indiana Geographic Information Office','title':'Indiana 2016-2020 bare-earth DEM ImageServer','url':'https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_2016_2020_DEM/ImageServer/identify','product':'State 2.5 ft bare-earth/interpolated DEM; queried by point at 36 interior sample locations.'},
 'footprint_source':{'provider':'Purdue Campus GIS','service':'BuildingShapesZip4 FeatureServer, layer 0','feature_id':54,'building_code':'KRAN','raw_snapshot':'audit/batch2_krannert/krannert_gis_fid54_4326.json','native_crs':'EPSG:3857','saved_boundary_crs':'EPSG:4326','method':'Original GIS polygon transformed to DSM raster CRS by rasterio; valid pixel centers selected inside polygon. No geometry fit or model footprint used.'},
 'dsm_summary':dsm_info,'terrain_samples':samples,'terrain_summary_ftUS':{'count':len(terrain),'min':float(np.min(terrain)),'median':ground_med,'max':float(np.max(terrain))},
 'roof_surface_agl_ftUS':{'median':agl,'p10_p90':[quant_agl['p10'],quant_agl['p90']],'quantiles':quant_agl,'interpretation':'The median DSM-minus-sampled-DEM difference is an indicative typical surface height above nearby interpolated bare earth. The wide distribution includes lower/stepped surfaces, roof edges, voids and equipment; it is not a single surveyed roof/parapet/penthouse height.'},
 'model_datums_ft_agl':model,
 'comparison':{'roof_surface_median_vs_model_roof_deck_ft':agl-model['roof_deck'],'roof_surface_p90_vs_model_parapet_ft':quant_agl['p90']-model['parapet_top'],'roof_surface_max_vs_model_overrun_ft':quant_agl['p100']-model['elevator_overrun_top'],'assessment':'Compare LiDAR only as an independent broad vertical plausibility check. Do not interpret DSM surface statistics as measuring named model levels or prove the GIS vertical fields R/Extrution. The point DEM is interpolated beneath the building and project-to-GIS positioning is approximate.'},
 'limits':['5 ft DSM raster cells limit pinpoint attribution to roof elements.','DSM includes top surfaces and equipment rather than bare earth; the polygon samples roof planes, stepped levels, edges and possible voids.','The 2.5 ft DTM values are point-query interpolations under the building, not surveyed foundation or grade elevations.','The project-local coordinate transform is approximate; there is no as-built elevation drawing or surveyed vertical datum in this audit.','This cannot establish occupied floor count, exact parapet/penthouse height, or undocumented GIS field semantics.'],
 'asset_geometry_changed':False,'saved_source_reopen_validation':'Existing audit/batch2_krannert/validation_round4.json is still the latest saved-source reopen validation; this r7 analysis changed evidence only.'
}
OUT.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'output':str(OUT),'dsm_valid_cells':len(vals),'dsm_median_ftUS':dsm_med,'dtm_count':len(terrain),'dtm_median_ftUS':ground_med,'median_surface_agl_ftUS':agl,'p10_p90_agl_ftUS':[quant_agl['p10'],quant_agl['p90']]},indent=2))

