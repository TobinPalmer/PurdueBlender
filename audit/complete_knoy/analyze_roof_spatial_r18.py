import json, math, sys
from pathlib import Path
_SCRIPT_DIR=Path(__file__).resolve().parent
sys.path=[e for e in sys.path if Path(e or ".").resolve()!=_SCRIPT_DIR]
import numpy as np, rasterio
from rasterio.warp import transform
root=Path.cwd(); audit=root/'audit/complete_knoy'; tif=audit/'indiana_3dep_2018_dsm_in2018_30001885_12.tif'
gis=json.loads((root/'modular/buildings/target_buildings_gis.json').read_text())['KNOY']['world_polygon']
def inside(x,y):
    hit=False
    for i,(x1,y1) in enumerate(gis):
        x2,y2=gis[(i+1)%len(gis)]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1: hit=not hit
    return hit
def local_to_ll(x,y): return -86.9137+x/84810.60416539927,40.4274+y/111040.0
def ll_to_local(lon,lat): return (lon+86.9137)*84810.60416539927,(lat-40.4274)*111040.0
with rasterio.open(tif) as ds:
    a=ds.read(1); rows,cols=np.indices(a.shape); px,py=rasterio.transform.xy(ds.transform,rows,cols,offset='center');
    lon,lat=transform(ds.crs,'EPSG:4326',list(np.asarray(px).ravel()),list(np.asarray(py).ravel()))
    xs,ys=zip(*(ll_to_local(lon[i],lat[i]) for i in range(len(lon))))
    valid=[]
    for i,v in enumerate(a.ravel()):
        if np.isfinite(v) and v>0 and inside(xs[i],ys[i]): valid.append((float(v)-621.06,xs[i]-218.38949585,ys[i]-44.11999893,int(i)))
valid.sort(reverse=True)
# Report p99+ cell set and whether those cells overlap the schematic penthouse footprint.
top=[{'height_agl_ft':round(h,2),'asset_local_x_m':round(x,2),'asset_local_y_m':round(y,2),'inside_penthouse_bbox':-6.89<=x<=8.11 and -16.12<=y<=3.88} for h,x,y,i in valid if h>=np.percentile([v[0] for v in valid],99)]
report={'dataset':'Indiana 2018 3DEP DSM 5ft cells, acquisition 2018-04-20','source_file':str(tif.relative_to(root)),'approx_bare_earth_reference_ft':621.06,'valid_cells':len(valid),'agl_quantiles_ft':{str(q):round(float(np.percentile([v[0] for v in valid],q)),2) for q in (50,75,90,95,99,100)},'current_model_penthouse_bbox_asset_local_xy_m':[-6.89,8.11,-16.12,3.88],'top_percentile_cells':top,'limits':['The GIS-to-raster conversion follows the project approximate local geographic frame and 5 ft DSM raster transform.','The bare-earth reference is the previous 21-point median, not a surveyed base elevation.','DSM cells include roof surfaces and elevated objects and cannot identify a penthouse by themselves.','The model penthouse bbox comparison is a schematic candidate only; no fit/alignment is asserted.']}
(audit/'roof_spatial_check_r18.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))

