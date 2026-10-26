"""Measure the Purdue GIS CQNE footprint against Indiana's 2013 NDHM tile."""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from pyproj import Transformer
from shapely.geometry import Point, Polygon

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "audit/massing_cary_quadrangle_northeast_cqne_0a76fca/sources"
RASTER = SRC / "indiana_2013_ndhm_tile_29951885.tif"
GIS = SRC / "purdue_gis_feature_638_cqne_4326.json"
OUT = ROOT / "audit/massing_cary_quadrangle_northeast_cqne_0a76fca/ndhm_measurement.json"
PNG = ROOT / "audit/massing_cary_quadrangle_northeast_cqne_0a76fca/ndhm_cqne_profile.png"

arr = np.asarray(Image.open(RASTER), dtype=float)
feature = json.loads(GIS.read_text(encoding="utf-8"))["features"][0]
ring = feature["geometry"]["rings"][0]
to_sp = Transformer.from_crs(4326, 2966, always_xy=True)
poly = Polygon([to_sp.transform(lon, lat) for lon, lat in ring])
px, x0, y0 = 5.0, 2995000.0, 1890000.0  # TIFF GeoTIFF tags: 5 ft pixels; upper-left tiepoint.
minx, miny, maxx, maxy = poly.bounds
c0 = max(0, int((minx - x0) / px) - 1)
c1 = min(arr.shape[1], int((maxx - x0) / px) + 2)
r0 = max(0, int((y0 - maxy) / px) - 1)
r1 = min(arr.shape[0], int((y0 - miny) / px) + 2)
samples = []
for r in range(r0, r1):
    y = y0 - (r + 0.5) * px
    for c in range(c0, c1):
        x = x0 + (c + 0.5) * px
        if poly.contains(Point(x, y)):
            v = float(arr[r, c])
            if -1.0 < v < 150.0:
                samples.append({"row": r, "col": c, "x_spw_ft": x, "y_spw_ft": y,
                                "ndhm_native_value": v})
vals = np.array([s["ndhm_native_value"] for s in samples])
qs = {str(int(q * 100)): float(np.quantile(vals, q)) for q in (0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99)}
profile = []
for i in range(12):
    yc = miny + (i + 0.5) * (maxy - miny) / 12
    band = np.array([s["ndhm_native_value"] for s in samples
                     if abs(s["y_spw_ft"] - yc) <= (maxy - miny) / 24])
    profile.append({"cross_building_band": i + 1,
                    "median_ndhm_native": float(np.median(band)) if len(band) else None,
                    "sample_count": int(len(band))})
result = {
    "building_id": "massing_cary_quadrangle_northeast_cqne_0a76fca",
    "source": {
        "provider": "Indiana 3DEP LiDAR products hosted by Purdue GDSL/iDiF; AWS open-data bucket",
        "url": "https://giselevationingov.s3.us-east-2.amazonaws.com/ndhmoptimized/statewide/2013/SPW/5ft/in2013_29951885_12_ndhm.tif",
        "product_definition_url": "https://gdsl.org/2021/08/02/how-to-add-indiana-lidar-data-product-layers-in-gis-software/",
        "retrieved": "2026-10-26",
        "source_date": "2011-2013 statewide Indiana LiDAR program; tile key identifies 2013; exact flight date not specified in file metadata",
        "crs": "NAD83 / Indiana West (ftUS), EPSG:2966 (GeoTIFF geokeys)",
        "horizontal_resolution": "5 US survey feet (1000 x 1000 cells per 5000-foot tile)",
        "vertical_product": "Normalized Digital Height Model: surface/object height above underlying ground; provider states 5-ft GSD",
        "vertical_unit_limit": "The tile declares the horizontal CRS unit as US survey feet but does not explicitly declare the raster value unit. Values are retained in native units; feet-to-meter values below are interpretations, not surveyed measurements.",
        "license": "Indiana Statewide Elevation Catalog states CC0; URL https://registry.opendata.aws/in-elevation/"
    },
    "mask": {
        "feature_id": 638,
        "input_geometry": "Purdue BuildingShapesZip4 Feature 638 exact CQNE ring in WGS84",
        "transform": "WGS84 to EPSG:2966 using PROJ/PyProj; no local degree approximation for raster sampling",
        "pixels_inside_footprint": int(len(vals)),
        "pixel_center_mask": "centers of 5-ft raster cells inside the transformed GIS polygon",
    },
    "native_height_summary": {"minimum": float(vals.min()), "maximum": float(vals.max()),
                               "quantiles": qs,
                               "if_native_values_are_US_survey_feet_quantile_m": {
                                   k: round(v * 0.3048006096, 3) for k, v in qs.items()}},
    "cross_section": {
        "axis": "12 equal-width bands across the short footprint axis (south to north)",
        "median_height_by_band_native_units": profile,
        "interpretation": "central bands are higher than outer bands, supporting a longitudinal gable roof profile; narrow-pixel sampling and unknown vertical unit leave pitch and eave exact values unverified"
    },
    "uncertainty": [
        "The 2013 statewide tile has 5-ft cell spacing; each cell averages roof and edge effects.",
        "No explicit vertical-unit or accuracy field is embedded in this normalized-height tile; retained raw native values and labeled conversion avoid presenting an estimate as a measurement.",
        "The vertical source predates the 2000-2006 Cary renovation; external roof height/form are assumed unchanged only at broad-massing level.",
        "The footprint mask comes from an independent Purdue facility GIS record and can include overhang/outline differences."
    ],
    "sample_values": samples
}
OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

# Top-down footprint height evidence, preserving the 5-ft cells.
crop = arr[r0:r1, c0:c1]
scale = 8
im = Image.new("RGB", (crop.shape[1] * scale, crop.shape[0] * scale), (230, 230, 225))
draw = ImageDraw.Draw(im)
for rr in range(crop.shape[0]):
    for cc in range(crop.shape[1]):
        v = float(crop[rr, cc])
        t = max(0.0, min(1.0, (v - 30.0) / 30.0))
        color = (int(35 + 205*t), int(75 + 65*(1-t)), int(190 - 160*t))
        draw.rectangle((cc*scale, rr*scale, (cc+1)*scale-1, (rr+1)*scale-1), fill=color)
pts = []
for lon, lat in ring:
    x, y = to_sp.transform(lon, lat)
    pts.append(((x - x0) / px - c0, (y0 - y) / px - r0))
poly_px = [(round(x*scale), round(y*scale)) for x,y in pts]
draw.line(poly_px + [poly_px[0]], fill=(20,20,20), width=2*scale)
im.save(PNG)
print(json.dumps({"samples":len(vals),"quantiles_native":qs,"png":str(PNG),"report":str(OUT)},indent=2))
