"""Analyze the public 2018 Indiana 3DEP DSM at the Math Sciences footprint."""
import json
from pathlib import Path
import numpy as np
import rasterio
from PIL import Image, ImageDraw
from rasterio.warp import transform, reproject, Resampling
from rasterio.transform import xy

ROOT = Path(r"C:/Users/Tobin/Documents/Blender/PurdueMap")
TIF = ROOT / "audit/batch3_math/indiana_3dep_2018_dsm_in2018_29951885_12_dsm.tif"
DTM = ROOT / "audit/batch3_math/indiana_3dep_2018_dtm_in2018_29951885_12.tif"
GEOJSON = ROOT / "audit/batch3_math/gis_fid227.geojson"
OUT = ROOT / "audit/batch3_math/math_roof_dsm_r10.json"
PNG = ROOT / "audit/batch3_math/math_dsm_roof_height_r10.png"

feature = json.loads(GEOJSON.read_text(encoding="utf-8"))["features"][0]
ring = feature["geometry"]["coordinates"][0]
with rasterio.open(TIF) as ds:
  with rasterio.open(DTM) as dem:
    if ds.crs is None:
        raise RuntimeError("DSM has no CRS")
    lon, lat = zip(*ring)
    px, py = transform("EPSG:4326", ds.crs, list(lon), list(lat))
    h, w = ds.height, ds.width
    cols, rows = np.meshgrid(np.arange(w), np.arange(h))
    x, y = xy(ds.transform, rows, cols, offset="center")
    x = np.asarray(x).reshape(h,w); y = np.asarray(y).reshape(h,w)
    # Vectorized even-odd point-in-polygon mask in the DSM's projected CRS.
    inside = np.zeros((h,w), dtype=bool)
    x1,y1=px[-1],py[-1]
    for x2,y2 in zip(px,py):
        crosses = ((y1 > y) != (y2 > y)) & (x < (x2-x1)*(y-y1)/(y2-y1+1e-30)+x1)
        inside ^= crosses
        x1,y1=x2,y2
    data=ds.read(1,masked=True)
    values=np.asarray(data.filled(np.nan),dtype=np.float64)
    finite=np.isfinite(values)
    building=values[inside & finite]
    # This ring is nearby ground/context, not a building base survey; roofs,
    # tree canopy and elevated plazas can contaminate it.
    pix=ds.res[0]
    center_x=np.mean(px); center_y=np.mean(py)
    d2=(x-center_x)**2+(y-center_y)**2
    meters_per_us_survey_foot = 0.304800609601219
    ring_mask=(d2>(20/meters_per_us_survey_foot/pix)**2)&(d2<(60/meters_per_us_survey_foot/pix)**2)&(~inside)&finite
    context=values[ring_mask]
    dem_onto_dsm=np.full((h,w),np.nan,dtype=np.float32)
    reproject(source=rasterio.band(dem,1),destination=dem_onto_dsm,
      src_transform=dem.transform,src_crs=dem.crs,dst_transform=ds.transform,dst_crs=ds.crs,
      src_nodata=dem.nodata,dst_nodata=np.nan,resampling=Resampling.average)
    ground_inside=dem_onto_dsm[inside & np.isfinite(dem_onto_dsm)]
    ground_context=dem_onto_dsm[ring_mask & np.isfinite(dem_onto_dsm)]
    normalized=(values-dem_onto_dsm)
    height_cells=normalized[inside & np.isfinite(normalized)]
    high_rows,high_cols=np.where(inside & np.isfinite(normalized) & (normalized>125.0))
    hx,hy=xy(ds.transform,high_rows,high_cols,offset="center")
    hlon,hlat=transform(ds.crs,"EPSG:4326",list(hx),list(hy))
    lon0,lat0=-86.9137,40.4274
    mx,my=-181.119995,-126.905003
    lx=(np.asarray(hlon)-lon0)*111412.84*np.cos(np.deg2rad(lat0))-mx
    ly=(np.asarray(hlat)-lat0)*111040-my
    high_zone_local_bounds_m=[[float(np.min(lx)),float(np.max(lx))],[float(np.min(ly)),float(np.max(ly))]]
    high_zone_local_pixel_count=int(len(high_rows))
    r_idx,c_idx=np.where(inside)
    r0,r1=max(0,int(r_idx.min())-4),min(h,int(r_idx.max())+5)
    c0,c1=max(0,int(c_idx.min())-4),min(w,int(c_idx.max())+5)
    height_roi=normalized[r0:r1,c0:c1]
    mask_roi=inside[r0:r1,c0:c1]
    # A restrained qualitative hypsometric ramp for review, not a surface render.
    t=np.clip((height_roi-0.0)/150.0,0,1)
    rgb=np.empty((*height_roi.shape,3),dtype=np.uint8)
    stops=[(0.0,(55,85,145)),(0.18,(64,158,173)),(0.42,(216,211,121)),(0.78,(203,112,69)),(1.0,(130,52,45))]
    for (ta,ca),(tb,cb) in zip(stops[:-1],stops[1:]):
        sel=(t>=ta)&(t<=tb)
        u=((t[sel]-ta)/(tb-ta))[:,None]
        rgb[sel]=np.asarray(ca)+(np.asarray(cb)-np.asarray(ca))*u
    rgb[~mask_roi]=(232,232,232)
    px=Image.fromarray(rgb).resize((rgb.shape[1]*6,rgb.shape[0]*6),Image.Resampling.NEAREST)
    canvas=Image.new("RGB",(px.width,px.height+100),(250,250,248)); canvas.paste(px,(0,0))
    draw=ImageDraw.Draw(canvas)
    draw.text((12,px.height+12),"2018 DSM minus bare-earth DTM · Math GIS footprint · 5 ft cells",fill=(20,20,20))
    draw.text((12,px.height+42),"Color ramp 0–150 ft above terrain; main roof median 121.1 ft; high roof percentile 132.7 ft. Not architectural elevations.",fill=(20,20,20))
    canvas.save(PNG)
    count=int(building.size)
    result={
      "provider":"Indiana Geographic Information Office / Indiana Statewide 3DEP Lidar Dates MapServer and public 3DEP DSM object storage",
      "acquisition_project":"2018",
      "query_layer_tile":"in2018_29951885_12",
      "tile_acquisition_date_utc":"2018-04-20T00:00:00Z",
      "tile_index_query_url":"https://gisdata.in.gov/server/rest/services/Indiana_Statewide_3DEP_Lidar_Dates/MapServer/5/query?where=1%3D1&geometry=-86.915642%2C40.4261348&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=*&returnGeometry=false&f=pjson",
      "tile_path":str(TIF.relative_to(ROOT)).replace('\\','/'),
      "review_image":str(PNG.relative_to(ROOT)).replace('\\','/'),
      "tile_sha256":__import__('hashlib').sha256(TIF.read_bytes()).hexdigest(),
      "source_url":"https://giselevationingov.s3.us-east-2.amazonaws.com/dsmoptimized/statewide/2018/SPW/5ft/in2018_29951885_12_dsm.tif",
      "bare_earth_dtm_path":str(DTM.relative_to(ROOT)).replace('\\','/'),
      "bare_earth_dtm_url":"https://giselevationingov.s3.us-east-2.amazonaws.com/demoptimized/statewide/2018/SPW/2.5ft/in2018_29951885_12.tif",
      "bare_earth_dtm_sha256":__import__('hashlib').sha256(DTM.read_bytes()).hexdigest(),
      "tile_crs":ds.crs.to_string(),
      "tile_bounds_projected_native_units":[ds.bounds.left,ds.bounds.bottom,ds.bounds.right,ds.bounds.top],
      "pixel_size_native_units":list(ds.res),
      "tile_shape_pixels":[h,w],
      "value_unit_note":"Source tile coordinates are Indiana West US survey feet. Raster pixel values have no embedded unit tags; ft is corroborated by matching local DTM elevations (~623.9) to Purdue GIS MATH Elevation=623.3. Both 2018 DSM and bare-earth DTM are compared in the same tile/product coordinate framework. Vertical datum metadata remains unverified.",
      "footprint_source":"Purdue GIS BuildingShapesZip4 FID 227 MATH polygon from gis_fid227.geojson, transformed from EPSG:4326 into the DSM CRS.",
      "footprint_pixel_count":count,
      "footprint_surface_elevation_ft_percentiles":{f"p{p}":float(np.nanpercentile(building,p)) for p in [0,5,10,25,50,75,90,95,99,100]},
      "nearby_context_20_to_60m_elevation_ft_percentiles":{f"p{p}":float(np.nanpercentile(context,p)) for p in [5,25,50,75,95]},
      "footprint_above_context_median_ft":float(np.nanmedian(building)-np.nanmedian(context)),
      "bare_earth_dtm_footprint_ft_percentiles":{f"p{p}":float(np.nanpercentile(ground_inside,p)) for p in [5,25,50,75,95]},
      "bare_earth_dtm_context_ft_percentiles":{f"p{p}":float(np.nanpercentile(ground_context,p)) for p in [5,25,50,75,95]},
      "normalized_surface_height_dsm_minus_dtm_ft_percentiles":{f"p{p}":float(np.nanpercentile(height_cells,p)) for p in [0,5,10,25,50,75,90,95,99,100]},
      "normalized_surface_height_dsm_minus_dtm_m_percentiles":{f"p{p}":float(np.nanpercentile(height_cells,p))*meters_per_us_survey_foot for p in [0,5,10,25,50,75,90,95,99,100]},
      "higher_surface_zone_over_125ft_local_bounds_m":high_zone_local_bounds_m,
      "higher_surface_zone_over_125ft_pixel_count":high_zone_local_pixel_count,
      "local_coordinate_method":"Reproject DSM cell centers to WGS84 then apply the existing Math audit local-frame approximation also used in make_overlays.py. High-zone coordinates are approximate and not a cadastral alignment.",
      "limitation":"DSM is a 2018 first-surface model at 5 ft cells, not a building roof survey. DTM below building may be interpolated because it is bare-earth; this height difference is approximate, and the footprint mask includes passage, parapets, roof equipment and returns. 5ft cells cannot resolve thin aerials, exact parapet edges, individual panel geometry, or floor-to-floor heights. The two products are useful as a broad roof-height range, not as-built architectural elevations."
    }
OUT.write_text(json.dumps(result,indent=2),encoding="utf-8")
print(json.dumps(result,indent=2))
