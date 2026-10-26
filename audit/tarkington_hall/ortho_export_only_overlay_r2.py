"""Draw the delivered export-collection shell against the orthophoto and GIS."""
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import MultiPoint, Polygon
from shapely.ops import unary_union

out = Path(__file__).resolve().parent
feature = json.loads((out / "gis_feature_662.json").read_text(encoding="utf-8"))["feature"]
shell_data = json.loads((out / "shell_vertices_r2.json").read_text(encoding="utf-8"))["objects"]
membership = json.loads((out / "independent_membership_r2.json").read_text(encoding="utf-8"))
origin = (-591.6124877929688, 348.0)
lon0, lat0 = -86.9137, 40.4274
sx = 111412.84 * math.cos(math.radians(lat0))
sy = 111040.0
rings = feature["geometry"]["rings"]
gis_rings = [[((lon - lon0) * sx - origin[0], (lat - lat0) * sy - origin[1]) for lon, lat in ring]
             for ring in rings]
gis = Polygon(gis_rings[0], gis_rings[1:])
export_names = set(membership["export_object_names"])
parts = []
for record in shell_data:
    if record["name"] not in export_names:
        continue
    polygon = MultiPoint(record["vertices_xy"]).convex_hull
    if polygon.geom_type == "Polygon" and polygon.area > 0:
        parts.append(polygon)
model = unary_union(parts)
img = Image.open(out / "indiana_2023_ortho_r1.png").convert("RGBA")
w, h = img.size
bbox = (-86.922, 40.429, -86.918, 40.433)


def pixel(point):
    x, y = point
    lon = lon0 + (x + origin[0]) / sx
    lat = lat0 + (y + origin[1]) / sy
    return (round((lon - bbox[0]) / (bbox[2] - bbox[0]) * w),
            round((bbox[3] - lat) / (bbox[3] - bbox[1]) * h))


overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
draw = ImageDraw.Draw(overlay, "RGBA")
points = [pixel(point) for point in gis.exterior.coords]
draw.polygon(points, fill=(240, 55, 65, 50))
draw.line(points, fill=(208, 35, 55, 255), width=5, joint="curve")
for polygon in model.geoms if hasattr(model, "geoms") else [model]:
    points = [pixel(point) for point in polygon.exterior.coords]
    draw.line(points, fill=(0, 135, 255, 255), width=5, joint="curve")
img.alpha_composite(overlay)
result = img.convert("RGB")
draw = ImageDraw.Draw(result)
try:
    font = ImageFont.truetype("arial.ttf", 28)
except OSError:
    font = ImageFont.load_default()
draw.rectangle((15, 15, 1220, 62), fill=(255, 255, 255))
draw.text((28, 25),
          "Tarkington — 2023 Indiana Orthophoto | red = GIS FID 662; blue = Asset_tarkington_hall only",
          font=font, fill=(20, 30, 40))
result.save(out / "ortho_export_only_overlay_r2.png")
