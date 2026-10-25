"""Sample the existing LiDAR-derived roof-envelope vertices from the R5 NDHM.

This is an audit preprocessing step. It does not edit the .blend file.
Each source vertex receives a local 5x5-cell median from its existing height
band, blended with the zone median to suppress cell-edge noise. High-zone
>22m outliers are deliberately excluded.
"""
import json, math
from pathlib import Path
import numpy as np
import rasterio
from pyproj import Transformer
from rasterio.features import geometry_mask
from shapely.geometry import Polygon, Point, mapping
from shapely.ops import transform as shp_transform

ROOT=Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap\audit\complete_neil_armstrong")
with open(ROOT/"roof_vertices_r7.json",encoding="utf-8") as f: vertices=json.load(f)
with open(ROOT/"sources"/"gis_feature_642_20261024.json",encoding="utf-8-sig") as f: gis=json.load(f)
ds=rasterio.open(ROOT/"sources"/"tippecanoe_ndhm_clip_r5.tif")
nd=ds.read(1,masked=True)
valid=~np.ma.getmaskarray(nd)
heights=nd.filled(-9999).astype(float)*0.304800609601219
to_sp=Transformer.from_crs(3857,2968,always_xy=True)
to_merc=Transformer.from_crs(2968,3857,always_xy=True)
merc_to_ll=Transformer.from_crs(3857,4326,always_xy=True)
ll_to_merc=Transformer.from_crs(4326,3857,always_xy=True)
gis_geom=Polygon(gis["features"][0]["geometry"]["rings"][0])
gis_sp=shp_transform(lambda x,y,z=None:to_sp.transform(x,y),gis_geom)
gis_mask=geometry_mask([mapping(gis_sp)],out_shape=nd.shape,transform=ds.transform,invert=True)
cell_h=0.304800609601219
bands={"ARMS_R5_Coarse_LiDAR_wing_low":(14.0,18.0),
       "ARMS_R5_Coarse_LiDAR_wing_mid":(18.0,20.0),
       "ARMS_R5_Coarse_LiDAR_roof_high":(20.0,22.0)}
lat0,lon0=40.4274,-86.9137
marker_x,marker_y=-109.0,400.1893310546875
cos_lat=math.cos(math.radians(lat0))
stats=[]

def local_to_sp(x,y):
    lon=lon0+(float(x)+marker_x)/(111412.84*cos_lat)
    lat=lat0+(float(y)+marker_y)/111040.0
    mx,my=ll_to_merc.transform(lon,lat)
    return to_sp.transform(mx,my)

for zone in vertices["zones"]:
    name=zone["object"]
    lo,hi=bands[name]
    cap=hi
    if name.endswith("roof_high"):
        # R5 source audit found only two cells above 22m. Treat those as
        # unresolved spikes rather than silently turning them into a tower.
        cap=22.0
    allowed=gis_mask & valid & (heights>=lo) & (heights<cap)
    rows,cols=np.nonzero(allowed)
    vals=heights[rows,cols]
    smoothed=[]
    fallback_count=0
    entries=[]
    anchor=float(zone["median_top_m"])
    for v in zone["vertices"]:
        sx,sy=local_to_sp(v["x"],v["y"])
        rr,cc=ds.index(sx,sy)
        r0,r1=max(0,rr-2),min(nd.shape[0],rr+3)
        c0,c1=max(0,cc-2),min(nd.shape[1],cc+3)
        local_mask=allowed[r0:r1,c0:c1]
        local_vals=heights[r0:r1,c0:c1][local_mask]
        if local_vals.size==0:
            fallback_count+=1
            xcent=ds.transform.c+(cols+0.5)*ds.transform.a
            ycent=ds.transform.f+(rows+0.5)*ds.transform.e
            distances=np.hypot(xcent-sx,ycent-sy)
            nearest=np.argsort(distances)[:5]
            local_vals=vals[nearest]
        local_median=float(np.median(local_vals))
        # Blend the local robust sample with the class median. This removes
        # raster-cell noise while retaining the broad local elevation trend.
        h=float(np.clip(0.35*local_median+0.65*anchor,lo,cap))
        smoothed.append(h)
        entries.append({"index":int(v["index"]),"x":v["x"],"y":v["y"],
                        "z_before":v["z_before"],"z_after":h,"source_sample_count":int(local_vals.size)})
    zone["height_band_m"]=[lo,hi]
    zone["roof_surface_vertices"] = entries
    stats.append({"object":name,"band_m":[lo,hi],"upper_sample_cap_m":cap,
                  "vertex_count":len(entries),"height_min_m":float(min(smoothed)),
                  "height_median_m":float(np.median(smoothed)),"height_max_m":float(max(smoothed)),
                  "height_range_m":float(max(smoothed)-min(smoothed)),"nearest_band_fallback_vertices":fallback_count,
                  "method":"5x5 median of 5-ft NDHM cells in the same GIS-clipped height band, blended 35% local/65% R5 zone median to suppress cell-scale noise; nearest five same-band cells used only when a vertex window has no valid sample."})

out={"building_id":"neil_armstrong_hall","revision":"R7","parent_revision":"R6",
     "source_asset_sha256":vertices["asset_sha256"],
     "source_raster":"sources/tippecanoe_ndhm_clip_r5.tif",
     "raster_date":"2017-2019 (Tippecanoe 2018 NDHM product)","raster_resolution":"5 US survey ft (1.524m)",
     "source_crs":"EPSG:2968, NAD83(HARN)/Indiana West (ftUS); elevations converted to meters",
     "registration":"Existing R5 GIS FID 642/local transform and manifest marker; X east, Y north, Z up.",
     "height_sampling":"Each existing top vertex retains its XY; z is set to a 5x5-cell median within its existing R5 NDHM band, blended 35% local and 65% R5 band median. Zones remain clipped to the existing GIS/shell-derived polygons. High zone cells above 22m are excluded from sampling because R5 found only two and cannot distinguish localized equipment from raster outliers.",
     "uncertainty":"5-ft NDHM is a broad normalized surface; local cell variation can include roof equipment, vegetation, or classification noise. The blend suppresses pixel-scale variation and retains only the broad band trend. It does not identify exact roof planes, facade lines, trusses, overhangs, floors, or story count. Vertex heights form a generalized surface, not measured architectural slopes.",
     "zones":vertices["zones"],"summary":stats}
with open(ROOT/"roof_surface_samples_r7_smooth.json","w",encoding="utf-8") as f: json.dump(out,f,indent=2)
print(json.dumps(stats,indent=2))
