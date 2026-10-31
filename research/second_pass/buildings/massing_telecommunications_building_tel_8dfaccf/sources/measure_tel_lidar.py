import json,math,pathlib
import numpy as np, laspy
from pyproj import Transformer
from shapely.geometry import Polygon
from shapely import contains_xy
ROOT=pathlib.Path(__file__).resolve().parents[3]
AUDIT=ROOT/'audit/massing_telecommunications_building_tel_8dfaccf'
TILE=ROOT/'work/jnsn/in2018_29951885_12.copc.laz'
feat=json.loads((AUDIT/'sources/purdue_gis_fid199_tel.json').read_text(encoding='utf-8-sig'))['features'][0]
project=Transformer.from_crs(4326,2968,always_xy=True)
poly=Polygon([project.transform(lon,lat) for lon,lat in feat['geometry']['rings'][0]])
inner=poly.buffer(-3.0/0.3048006096012192); outer=poly.buffer(5.0/0.3048006096012192).difference(poly)
las=laspy.read(TILE); x=las.x; y=las.y; z=las.z; cls=las.classification
ib=inner.bounds; ob=outer.bounds
im=(cls==1)&(x>=ib[0])&(x<=ib[2])&(y>=ib[1])&(y<=ib[3]); cand=np.flatnonzero(im); ii=cand[contains_xy(inner,x[cand],y[cand])]
gm=(cls==2)&(x>=ob[0])&(x<=ob[2])&(y>=ob[1])&(y<=ob[3]); candg=np.flatnonzero(gm); gi=candg[contains_xy(outer,x[candg],y[candg])]
base=float(np.median(z[gi])); h=(np.asarray(z[ii],float)-base)*0.3048
q=lambda p:float(np.partition(h,min(len(h)-1,math.ceil(p*len(h))-1))[min(len(h)-1,math.ceil(p*len(h))-1)])
res={'asset_id':AUDIT.name,'source_file':TILE.name,'source_url':'https://lidar.digitalforestry.org/QL2_3DEP_LiDAR_IN/Tippecanoe_Co_2018_3DEP/Elev18_LAS1.4SPW_IN/copc/in2018_29951885_12.copc.laz','lidar_crs':'NAD83(HARN)/Indiana West ftUS EPSG:2968','vertical_datum':'NAVD88 Geoid12B ftUS','target_polygon':'Purdue BuildingShapesZip4 FID 199, WGS84 ring transformed to EPSG:2968','roof_surface_filter':'ASPRS class 1 returns inside footprint eroded 3 m','ground_filter':'ASPRS class 2 returns within 5 m external footprint buffer','class_counts':{str(i):int(np.sum(cls==i)) for i in np.unique(cls)},'footprint_interior_return_count':int(len(ii)),'ground_return_count':int(len(gi)),'ground_median_ftUS':base,'roof_height_median_m':q(.5),'roof_height_p95_m':q(.95),'roof_height_p99_m':q(.99),'roof_height_max_m':float(h.max()),'all_footprint_class1_median_m':float(np.median((np.asarray(z[ (cls==1)&(x>=poly.bounds[0])&(x<=poly.bounds[2])&(y>=poly.bounds[1])&(y<=poly.bounds[3]) ],float)-base)*0.3048)),'method':'Median class-1 surface elevation minus median class-2 ground in exterior buffer; 3m erosion applied in feetUS in EPSG:2968. Nearest-rank quantiles.','interpretation':'Roof height is an estimate from unclassified surface points; no class-6 building returns in tile. Interior central statistic can include remaining vegetation or non-roof returns; compare spread and orthophoto. GIS reports four levels but its Extrution/R fields have undocumented units.'}
(AUDIT/'sources'/'tel_lidar_height_measurement.json').write_text(json.dumps(res,indent=2),encoding='utf-8'); print(json.dumps(res,indent=2))
