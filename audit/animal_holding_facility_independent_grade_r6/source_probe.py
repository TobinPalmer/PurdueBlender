"""Independent recomputation from raw AHF GIS and NDHM snapshots (R5)."""
import json, math
from pathlib import Path
import numpy as np
from PIL import Image
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "audit/animal_holding_facility/sources"
ring = json.loads((SRC/"purdue_gis_fid266_2026-10-25_stateplane_2968.json").read_text(encoding="utf-8-sig"))["features"][0]["geometry"]["rings"][0][:-1]
raster = Image.open(SRC/"indiana_lidar_ndhm_tippecanoe_2018_tile_in2018_29951880_12.tif")
origin_x, origin_y, pix = 2995000.0, 1885000.0, 5.0
split_y = 1883168.8443683232
ft_to_m = 1200/3937
to_geo = Transformer.from_crs(2968,4326,always_xy=True)
def inside(x,y):
    hit=False
    for i,(x1,y1) in enumerate(ring):
        x2,y2=ring[(i+1)%len(ring)]
        if (y1>y)!=(y2>y) and x < (x2-x1)*(y-y1)/(y2-y1)+x1: hit=not hit
    return hit
samples={"north_main":[],"south_addition":[]}
for row in range(raster.height):
    y=origin_y-(row+.5)*pix
    for col in range(raster.width):
        x=origin_x+(col+.5)*pix
        if not inside(x,y): continue
        z=float(raster.getpixel((col,row)))
        if z<=-10: continue
        lon,lat=to_geo.transform(x,y)
        lx=(lon+86.9137)*111412.84*math.cos(math.radians(40.4274))
        ly=(lat-40.4274)*111040.0
        zone="north_main" if y>split_y else "south_addition"
        samples[zone].append((lx,ly,z*ft_to_m))
def fit(name, size):
    s=np.asarray(samples[name],dtype=float)
    origin=np.median(s[:,:2],axis=0)
    bins={}
    for x,y,z in s:
        key=(math.floor((x-origin[0])/size),math.floor((y-origin[1])/size))
        bins.setdefault(key,[]).append(float(z))
    centers=np.asarray([((ix+.5)*size,(iy+.5)*size,np.median(zs)) for (ix,iy),zs in bins.items()])
    design=np.column_stack((centers[:,0],centers[:,1],np.ones(len(centers))))
    coef=np.linalg.lstsq(design,centers[:,2],rcond=None)[0]
    residual=centers[:,2]-design@coef
    flat=centers[:,2]-np.median(centers[:,2])
    q=lambda a,p:float(np.quantile(a,p))
    return {"bins":len(centers),"slope_percent_xy":[round(float(coef[0]*100),3),round(float(coef[1]*100),3)],
      "flat_median_abs_residual_m":round(float(np.median(np.abs(flat))),4),
      "plane_median_abs_residual_m":round(float(np.median(np.abs(residual))),4),
      "height_p05_m":round(q(s[:,2],.05),3),"height_median_m":round(float(np.median(s[:,2])),4),"height_p95_m":round(q(s[:,2],.95),3)}
summary={}
for name in samples:
    z=np.asarray([v[2] for v in samples[name]])
    summary[name]={"n":len(z),"median_m":round(float(np.median(z)),6),
      "q25_m":round(float(np.quantile(z,.25)),6),"q75_m":round(float(np.quantile(z,.75)),6),
      "fits_by_bin_m":{str(size):fit(name,size) for size in (2.5,5.,7.5,10.)}}
# Independently recompute plan geometry from the source's geographic vertices.
geo=json.loads((SRC/"purdue_gis_fid266_2026-10-25.json").read_text(encoding="utf-8-sig"))
coords=geo["features"][0]["geometry"]["rings"][0][:-1]
local=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.) for lon,lat in coords]
p={"asset_commit":"c40be18b4f6c70ae8a101d84549b3c89f25c0db5","source_feature_id":266,
 "source_outline_vertex_count":len(local),"source_outline_bounds_m":[[min(x for x,y in local),max(x for x,y in local)],[min(y for x,y in local),max(y for x,y in local)]],
 "ndhm":{"provider":"Indiana 3DEP NDHM / Purdue Geospatial Data Science Lab","source_year":2018,"crs":"EPSG:2968 NAD83(HARN) Indiana West, US survey feet","grid":"5 ft","samples":summary},
 "roof_profile_interpretation":"Independent least-squares fits to binned medians confirm a south-zone Y trend near -4% across 2.5–10 m bins. A north/main slope is small and unstable. Raster is a normalized surface model; this does not prove structural roof pitch, eaves, or seam.",
 "source_files":["audit/animal_holding_facility/sources/purdue_gis_fid266_2026-10-25.json","audit/animal_holding_facility/sources/purdue_gis_fid266_2026-10-25_stateplane_2968.json","audit/animal_holding_facility/sources/indiana_lidar_ndhm_tippecanoe_2018_tile_in2018_29951880_12.tif","audit/animal_holding_facility/sources/indiana_2023_orthophoto_georef_2026-10-25.jpg"]}
out=Path(__file__).resolve().parent/"source_probe.json"
out.write_text(json.dumps(p,indent=2)+"\n",encoding="utf-8")
print(json.dumps(p,indent=2))

