"""Retrieve an Indiana 2023 orthophoto crop and overlay GIS/model footprint."""
from __future__ import annotations
import json
import math
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

AUDIT = Path(__file__).resolve().parent
ROOT = AUDIT.parents[1]
GIS = json.loads((AUDIT / "gis_feature_879_raw.json").read_text(encoding="utf-8"))
MODEL = json.loads((AUDIT / "independent_grade_r5_extract.json").read_text(encoding="utf-8"))
FEATURE = next(f for f in GIS["features"] if f["attributes"]["FID"] == 879)
GIS_RING = FEATURE["geometry"]["rings"][0]
SHELL = MODEL["replacement_meshes"]["upper_shell"]
TOP_Z = max(v[2] for v in SHELL["vertices_world_local"])
TOP_FACES = [
    face for face in SHELL["faces"]
    if all(abs(SHELL["vertices_world_local"][i][2] - TOP_Z) < 1e-5 for i in face)
]
if len(TOP_FACES) != 1:
    raise RuntimeError(f"Expected one planar upper-shell footprint face, found {len(TOP_FACES)}")
MODEL_RING_LOCAL = [SHELL["vertices_world_local"][i] for i in TOP_FACES[0]]

lat0, lon0 = 40.4274, -86.9137
x_per_lon = 111412.84 * math.cos(math.radians(lat0))
y_per_lat = 111040.0
origin_x, origin_y = -544.25, 42.425

def web_mercator(lon, lat):
    radius = 6378137.0
    x = radius * math.radians(lon)
    y = radius * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
    return x, y

all_lons = [p[0] for p in GIS_RING]
all_lats = [p[1] for p in GIS_RING]
center_lon = (min(all_lons) + max(all_lons)) / 2
center_lat = (min(all_lats) + max(all_lats)) / 2
lon_pad = 0.0011
lat_pad = 0.0009
corners = [web_mercator(center_lon + dx, center_lat + dy)
           for dx, dy in [(-lon_pad, -lat_pad), (lon_pad, lat_pad)]]
xmin, xmax = sorted([corners[0][0], corners[1][0]])
ymin, ymax = sorted([corners[0][1], corners[1][1]])
width, height = 1800, 1400
service = "https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_2023_Imagery/ImageServer"
params = {
    "bbox": f"{xmin},{ymin},{xmax},{ymax}",
    "bboxSR": "3857",
    "imageSR": "3857",
    "size": f"{width},{height}",
    "format": "png",
    "f": "image",
}
image_url = service + "/exportImage?" + urllib.parse.urlencode(params)
request = urllib.request.Request(image_url, headers={"User-Agent": "PurdueCampusBuildingGrader/1.0"})
with urllib.request.urlopen(request, timeout=60) as response:
    image_bytes = response.read()
image_path = AUDIT / "indiana_2023_orthophoto_r5.png"
image_path.write_bytes(image_bytes)

def world_local_to_mercator(point):
    x_local, y_local = point[0], point[1]
    campus_x, campus_y = origin_x + x_local, origin_y + y_local
    lon = lon0 + campus_x / x_per_lon
    lat = lat0 + campus_y / y_per_lat
    return web_mercator(lon, lat)

def pixel(x, y):
    return ((x - xmin) / (xmax - xmin) * width,
            (ymax - y) / (ymax - ymin) * height)

gis_px = [pixel(*web_mercator(lon, lat)) for lon, lat in GIS_RING]
model_px = [pixel(*world_local_to_mercator(v)) for v in MODEL_RING_LOCAL]
image = Image.open(image_path).convert("RGB")
draw = ImageDraw.Draw(image)
draw.line(gis_px + [gis_px[0]], fill=(255, 38, 36), width=5)
draw.line(model_px + [model_px[0]], fill=(24, 80, 255), width=3)
font = ImageFont.load_default()
draw.rectangle((8, 8, 780, 44), fill=(255, 255, 255))
draw.text((16, 17), "2023 Indiana orthophoto: red = GIS FID 879; blue = R5 upper-shell roof trace", fill=(0, 0, 0), font=font)
overlay_path = AUDIT / "indiana_2023_orthophoto_overlay_r5.png"
image.save(overlay_path)

center_x, center_y = web_mercator(center_lon, center_lat)
identify_params = {
    "geometry": json.dumps({"x": center_x, "y": center_y, "spatialReference": {"wkid": 3857}}),
    "geometryType": "esriGeometryPoint",
    "sr": 3857,
    "returnGeometry": "false",
    "returnCatalogItems": "true",
    "f": "json",
}
identify_url = service + "/identify?" + urllib.parse.urlencode(identify_params)
identify_request = urllib.request.Request(identify_url, headers={"User-Agent": "PurdueCampusBuildingGrader/1.0"})
with urllib.request.urlopen(identify_request, timeout=60) as response:
    identify_data = json.loads(response.read().decode("utf-8"))
report = {
    "service": service,
    "service_description_url": service + "?f=pjson",
    "service_description": "Indiana 2023 Imagery ImageServer, spring 2023 orthophotography, 4-band nominal 6-inch resolution, CC0.",
    "retrieved_utc": datetime.now(timezone.utc).isoformat(),
    "building_source": "Purdue GIS FID 879 / PKRW; direct polygon ring",
    "source_crs": "EPSG:4326 (GIS) transformed to EPSG:3857 image request and back to project local coordinates for footprint overlay",
    "project_conversion": {
        "x": "X=(longitude+86.9137)*111412.84*cos(radians(40.4274))",
        "y": "Y=(latitude-40.4274)*111040.0",
        "manifest_origin_xy_m": [origin_x, origin_y],
    },
    "image_extent_3857": [xmin, ymin, xmax, ymax],
    "image_px": [width, height],
    "source_image": str(image_path),
    "overlay_image": str(overlay_path),
    "identify_response": identify_data,
    "limitations": [
        "This orthophoto validates roof footprint alignment, not surveyed wall-face dimensions.",
        "The project local XY conversion is approximate rather than survey control.",
    ],
}
(AUDIT / "indiana_2023_orthophoto_evidence_r5.json").write_text(
    json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
)
print(json.dumps({k: v for k, v in report.items() if k != "identify_response"}, indent=2, ensure_ascii=False))
