from __future__ import annotations
import json, math, urllib.parse, urllib.request, sys
from pathlib import Path
# The Knoy audit folder has inspect.py; remove that directory from import search so it does not shadow stdlib inspect.
_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path = [entry for entry in sys.path if Path(entry or ".").resolve() != _SCRIPT_DIR]
import numpy as np
import rasterio
from rasterio.features import geometry_mask
from rasterio.warp import transform

ROOT = Path(__file__).resolve().parents[2]
AUDIT = Path(__file__).resolve().parent
DSM = AUDIT / 'indiana_3dep_2018_dsm_in2018_30001885_12.tif'
GIS = ROOT / 'modular/buildings/target_buildings_gis.json'
REPORT = AUDIT / 'roof_height_assessment_r8.json'
SVG = AUDIT / 'knoy_roof_height_vertical_evidence_r8.svg'

props = json.loads(GIS.read_text(encoding='utf-8'))['KNOY']
polygon = props['world_polygon']
# Project-local campus conversion from the documented project frame. It is
# approximate rather than a surveyed CRS transformation.
def local_to_lonlat(x, y):
    return -86.9137 + x / 84810.60416539927, 40.4274 + y / 111040.0

def inside(x, y):
    hit = False
    for i, (x1, y1) in enumerate(polygon):
        x2, y2 = polygon[(i + 1) % len(polygon)]
        if (y1 > y) != (y2 > y) and x < (x2-x1)*(y-y1)/(y2-y1)+x1:
            hit = not hit
    return hit

lons = [local_to_lonlat(x, y)[0] for x, y in polygon]
lats = [local_to_lonlat(x, y)[1] for x, y in polygon]
with rasterio.open(DSM) as ds:
    xs, ys = transform('EPSG:4326', ds.crs, lons, lats)
    projected = list(zip(xs, ys))
    feature = {'type':'Polygon','coordinates':[projected + [projected[0]]]}
    arr = ds.read(1)
    mask = geometry_mask([feature], out_shape=arr.shape, transform=ds.transform, invert=True, all_touched=False)
    vals = arr[mask & np.isfinite(arr) & (arr > 0)]
    if not len(vals): raise RuntimeError('No valid DSM pixels intersect KNOY footprint')
    hist_edges = np.arange(math.floor(float(vals.min())), math.ceil(float(vals.max())) + 1.0, 1.0)
    hist_counts, _ = np.histogram(vals, bins=hist_edges)
    dominant_idx = int(np.argmax(hist_counts))
    dsm_stats = {
        'valid_cell_centers_within_approx_gis_footprint': int(len(vals)),
        'elevation_ft_quantiles_p10_p25_p50_p75_p90_p95_p99_max': [float(x) for x in np.percentile(vals, [10,25,50,75,90,95,99,100])],
        'dominant_surface_bin_1ft_range': [float(hist_edges[dominant_idx]), float(hist_edges[dominant_idx+1])],
        'dominant_surface_bin_cell_count': int(hist_counts[dominant_idx]),
        'dominant_surface_bin_share': float(hist_counts[dominant_idx] / len(vals)),
        'approx_projected_footprint_bounds_ft': [float(min(xs)), float(min(ys)), float(max(xs)), float(max(ys))],
        'raster_crs': ds.crs.to_wkt(),
        'raster_transform': [float(v) for v in ds.transform[:6]],
        'raster_shape_px': [int(ds.height), int(ds.width)],
        'raster_pixel_size_ft': [abs(float(ds.transform.a)), abs(float(ds.transform.e))],
        'raster_nodata': ds.nodata,
        'raster_file_bytes': DSM.stat().st_size,
    }

# 5x5 interior test grid; point-query the official state bare-earth DEM at
# each point. This estimates terrain datum beneath the roof, not structure base.
min_x, max_x = min(x for x,y in polygon), max(x for x,y in polygon)
min_y, max_y = min(y for x,y in polygon), max(y for x,y in polygon)
samples=[]
for iy in range(1,6):
    for ix in range(1,6):
        x=min_x+(max_x-min_x)*ix/6
        y=min_y+(max_y-min_y)*iy/6
        if not inside(x,y): continue
        lon,lat=local_to_lonlat(x,y)
        geom=json.dumps({'x':lon,'y':lat,'spatialReference':{'wkid':4326}},separators=(',',':'))
        query=urllib.parse.urlencode({'geometry':geom,'geometryType':'esriGeometryPoint','sr':'4326','returnGeometry':'false','f':'json'})
        service='https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_2016_2020_DEM/ImageServer/identify'
        with urllib.request.urlopen(service+'?'+query,timeout=30) as response: result=json.load(response)
        val=float(result['value'])
        samples.append({'local_xy_m':[round(x,3),round(y,3)],'latitude':lat,'longitude':lon,'bare_earth_elevation_ft':val})

terrain=np.array([s['bare_earth_elevation_ft'] for s in samples],dtype='float64')
dsm_median=float(np.median(vals)); ground_median=float(np.median(terrain)); agl_median=dsm_median-ground_median
p10,p25,p75,p90=(float(x)-ground_median for x in np.percentile(vals,[10,25,75,90]))
# model datums read from the saved source in Blender's reopen validation,
# independently recorded here in feet for a compact, legible comparison.
model_datums=[('L1 datum',0.0,'supported as model origin / base reference'),('L2 slab top',4.481*3.280839895,'2018 plan supports L1-L4 interval'),('L3 slab top',8.961*3.280839895,'2018 plan supports L1-L4 interval'),('L4 slab top',13.442*3.280839895,'2018 plan supports L1-L4 interval'),('L5 slab top',17.922*3.280839895,'retained slab; story function unresolved')]
report={
 'revision':8,'assessment':'Indicative roof-surface height from statewide 3DEP; no modeled height or geometry changed.',
 'dsm_source':{'provider':'Indiana Geographic Information Office / Indiana Statewide Elevation Catalog','title':'Indiana 2016-2020 QL2 3DEP LiDAR, 2018 Tippecanoe tile','tile':'in2018_30001885_12','acquisition_date':'2018-04-20','download_url':'https://giselevationingov.s3.us-east-2.amazonaws.com/dsmoptimized/statewide/2018/SPW/5ft/in2018_30001885_12.tif','dataset_catalog':'https://registry.opendata.aws/in-elevation/','product':'dsmoptimized raster, 5 ft cells, float elevations in US survey feet in NAD83(HARN) / Indiana West (ftUS).','license':'CC0'},
 'terrain_source':{'provider':'Indiana Geographic Information Office','title':'Indiana 2016-2020 bare-earth DEM ImageServer','url':'https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_2016_2020_DEM/ImageServer','pixels':'2.5 ft statewide product; 21 point samples queried at interior points of the approximate Knoy GIS polygon.'},
 'footprint_registration':{'source':'modular/buildings/target_buildings_gis.json / KNOY world_polygon','conversion':'project-local x/y to lon/lat using x=(lon+86.9137)*84810.60416539927 m/deg and y=(lat-40.4274)*111040 m/deg, then raster CRS transform','caution':'Project-local conversion is approximate; the 5ft DSM grid and building outline are not an as-built survey.'},
 'dsm_footprint_stats':dsm_stats,
 'dtm_samples':samples,
 'terrain_summary_ft':{'count':len(samples),'min':float(np.min(terrain)),'median':ground_median,'max':float(np.max(terrain))},
 'roof_surface_inference_ft':{'representative_surface_elevation_median_ft':dsm_median,'approx_bare_earth_median_ft':ground_median,'representative_surface_above_bare_earth_ft':agl_median,'whole_footprint_surface_distribution_agl_p10_p25_p75_p90_ft':[p10,p25,p75,p90],'interpretation':'The DSM median within the approximate GIS footprint is about 60 ft above the sampled bare-earth median. The broad percentile spread reflects stepped surfaces, edges, openings/voids and elevated equipment; it is a height check, not one roof plane or parapet elevation.'},
 'model_datums_ft_agl':[{'datum':name,'height_ft':round(z,2),'evidence_status':status} for name,z,status in model_datums],
 'comparison':'The indicative 2018 DSM median roof-surface height (~60 ft AGL) is close to the inherited model L5 slab datum (~58.8 ft). It makes a roof-level slab interpretation plausible but cannot establish that L5 is a roof slab, an occupied floor, or exactly registered in vertical datum. The GIS extraction attribute of 48 ft remains conflicting and its semantics are not surveyed height.',
 'limitations':['5 ft DSM cell spacing and approximate footprint conversion limit local feature attribution.','The DSM median combines roof planes, lower surfaces, edges and rooftop objects; it does not measure the parapet, penthouse, or a specific facade point.','The bare-earth surface is modeled/interpolated under the building; the 21 samples are service queries inside the footprint, not surveyed building footings.','Absolute accuracy specifications for QL2 are statewide metrics, not a Knoy-specific accuracy assessment.','The 2018 surface snapshot does not prove 2026 roof configuration.','This assessment does not register the PV mesh to the 2023 orthophoto; withdrawn cyan PV bounds remain do-not-use.'],
 'geometry_changed':False,
}
REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

# A simple elevation-band chart so reviewers can see which model slabs are
# supported by the plan and how the LiDAR roof estimate relates to L5.
W,H=1440,1040
x0,x1=115,750; ybase=815; px_per_ft=5.0
Y=lambda v: ybase-v*px_per_ft
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
'<rect width="100%" height="100%" fill="#f6f7f8"/>',
'<text x="64" y="72" font-family="Arial, sans-serif" font-size="34" font-weight="700" fill="#20272b">Knoy Hall · vertical evidence check</text>',
'<text x="64" y="109" font-family="Arial, sans-serif" font-size="19" fill="#4b565c">2018 3DEP surface model compared with saved slab datums · approximate, not an as-built survey</text>',
'<rect x="64" y="142" width="1312" height="72" rx="10" fill="#fff2d6" stroke="#d0a553" stroke-width="2"/>',
'<text x="88" y="174" font-family="Arial, sans-serif" font-size="19" font-weight="700" fill="#684b13">No roof/L5 geometry changed.</text>',
'<text x="88" y="199" font-family="Arial, sans-serif" font-size="17" fill="#684b13">The LiDAR roof-surface median is near the retained L5 slab, but cannot tell whether that slab is a roof deck or occupied story.</text>',
'<text x="80" y="252" font-family="Arial, sans-serif" font-size="18" font-weight="700" fill="#26343a">Height above approximate terrain datum (ft)</text>']
# grid / axis
for h in range(0,101,10):
 y=Y(h); svg.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="#d9dfe2" stroke-width="1"/>');svg.append(f'<text x="{x0-22}" y="{y+6:.1f}" text-anchor="end" font-family="Arial" font-size="15" fill="#536067">{h}</text>')
# Area distribution for whole-footprint DSM elevations above median sampled bare earth, p10 to p90.
ylo,yhi=Y(p90),Y(p10)
svg += [f'<rect x="{x0+190}" y="{ylo:.1f}" width="280" height="{yhi-ylo:.1f}" fill="#a9c7df" opacity="0.5" stroke="#517c9c" stroke-width="2"/>',
 f'<text x="{x0+330}" y="{ylo-10:.1f}" text-anchor="middle" font-family="Arial" font-size="16" fill="#2f5977">2018 DSM footprint p10–p90: {p10:.1f}–{p90:.1f} ft AGL</text>']
# level datums
levels=[('L1',0.0,'#42525a'),('L2',4.481*3.280839895,'#456f90'),('L3',8.961*3.280839895,'#456f90'),('L4',13.442*3.280839895,'#456f90'),('L5 slab — unresolved',17.922*3.280839895,'#a63d37')]
for name,h,col in levels:
 y=Y(h);dash=' stroke-dasharray="10 8"' if name.startswith('L5') else ''
 svg.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="{col}" stroke-width="3"{dash}/>')
 svg.append(f'<text x="{x0+10}" y="{y-7:.1f}" font-family="Arial" font-size="16" font-weight="700" fill="{col}">{name} · {h:.1f} ft</text>')
# LiDAR median line and GIS attribute
h=agl_median;y=Y(h)
svg += [f'<line x1="{x0+180}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="#d98218" stroke-width="4"/>',f'<text x="{x1-2}" y="{y-14:.1f}" text-anchor="end" font-family="Arial" font-size="17" font-weight="700" fill="#9d5e0a">DSM median surface ≈ {h:.1f} ft AGL</text>']
y=Y(48);svg += [f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="#71797e" stroke-width="2" stroke-dasharray="5 8"/>',f'<text x="{x1-2}" y="{y-8:.1f}" text-anchor="end" font-family="Arial" font-size="15" fill="#596167">GIS extraction attribute: 48 ft (semantics unresolved)</text>']
# Evidence summary to the right of the common-height chart.
svg += [
'<rect x="805" y="250" width="555" height="575" rx="14" fill="#ffffff" stroke="#ccd4d8" stroke-width="2"/>',
'<text x="835" y="292" font-family="Arial" font-size="23" font-weight="700" fill="#26343a">Evidence and reading</text>',
'<text x="835" y="334" font-family="Arial" font-size="17" font-weight="700" fill="#33464f">2018 Indiana 3DEP surface model</text>',
'<text x="835" y="363" font-family="Arial" font-size="16" fill="#3f4c52">DSM median: 680.94 ft elevation</text>',
'<text x="835" y="389" font-family="Arial" font-size="16" fill="#3f4c52">Bare-earth median: 621.06 ft (21 queries)</text>',
'<text x="835" y="415" font-family="Arial" font-size="16" font-weight="700" fill="#9d5e0a">Indicative difference: 59.9 ft</text>',
'<line x1="835" y1="440" x2="1330" y2="440" stroke="#e0e5e8"/>',
'<text x="835" y="475" font-family="Arial" font-size="17" font-weight="700" fill="#33464f">What the comparison supports</text>',
'<text x="835" y="505" font-family="Arial" font-size="16" fill="#3f4c52">The typical roof-like surface is close to the</text>',
'<text x="835" y="530" font-family="Arial" font-size="16" fill="#3f4c52">model L5 slab datum (58.8 ft), so a roof-level</text>',
'<text x="835" y="555" font-family="Arial" font-size="16" fill="#3f4c52">slab is plausible. The L5 story label remains</text>',
'<text x="835" y="580" font-family="Arial" font-size="16" fill="#3f4c52">unverified. The GIS 48 ft field conflicts.</text>',
'<line x1="835" y1="605" x2="1330" y2="605" stroke="#e0e5e8"/>',
'<text x="835" y="640" font-family="Arial" font-size="17" font-weight="700" fill="#33464f">Limits</text>',
'<text x="835" y="670" font-family="Arial" font-size="16" fill="#3f4c52">5 ft DSM cells, approximate footprint conversion,</text>',
'<text x="835" y="695" font-family="Arial" font-size="16" fill="#3f4c52">stepped surfaces and interpolated terrain. Not an</text>',
'<text x="835" y="720" font-family="Arial" font-size="16" fill="#3f4c52">as-built roof/parapet/penthouse height survey.</text>',
'<text x="835" y="758" font-family="Arial" font-size="16" fill="#3f4c52">Stairs remain illustrative; no continuous L1–roof</text>',
'<text x="835" y="783" font-family="Arial" font-size="16" fill="#3f4c52">route is source-verified. 2023 PV imagery is</text>',
'<text x="835" y="808" font-family="Arial" font-size="16" fill="#3f4c52">presence-only; the retracted mesh fit is not used.</text>'
]
# Context labels
svg += [f'<text x="{x0+10}" y="{Y(0)+21:.1f}" font-family="Arial" font-size="15" fill="#536067">L1 / sampled terrain reference</text>',
'<text x="80" y="862" font-family="Arial" font-size="16" fill="#37434a">2018 Purdue planning study: existing Levels 1–4, each 14′-8″ floor-to-floor.</text>',
'<text x="80" y="888" font-family="Arial" font-size="16" fill="#37434a">Model L1–L4 intervals track that study within about 0.01 m; L5 is a retained unverified slab, not a confirmed fifth story.</text>',
'<rect x="80" y="925" width="1280" height="74" rx="9" fill="#eef2f4" stroke="#c5cdd1"/>',
'<text x="102" y="954" font-family="Arial" font-size="16" fill="#36434a">2018 tile: in2018_30001885_12 · DSM 5 ft cells · 1,126 valid pixel centers within approximate GIS polygon. Terrain: 21 Indiana bare-earth DEM point queries.</text>',
'<text x="102" y="981" font-family="Arial" font-size="15" fill="#536067">DSM distribution is not a confidence interval; the surface includes lower steps, edges and equipment. PV image/bounds are not used for this height analysis.</text>',
'</svg>']
SVG.write_text('\n'.join(svg),encoding='utf-8')
print(json.dumps({'report':str(REPORT),'svg':str(SVG),'dsm_pixels':len(vals),'dsm_median_ft':dsm_median,'dtm_samples':len(samples),'dtm_median_ft':ground_median,'median_surface_agl_ft':agl_median,'dsm_p10_p90_agl_ft':[p10,p90]},indent=2))
