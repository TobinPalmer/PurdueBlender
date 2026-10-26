"""Make a review-only overlay of the official Purdue outline on the saved ortho."""
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "audit/animal_holding_facility/sources/purdue_gis_fid266_2026-10-25.json"
PHOTO = ROOT / "audit/animal_holding_facility/sources/indiana_2023_orthophoto_georef_2026-10-25.jpg"
OUT = ROOT / "audit/animal_holding_facility/orthophoto_footprint_overlay.png"
EXTENT = (-9675297.9304, 4926877.1, -9675197.8536, 4927002.196)
W, H = 1200, 1500
R = 6378137.0

data = json.loads(SOURCE.read_text(encoding="utf-8"))
ring = data["features"][0]["geometry"]["rings"][0]
pts = []
for lon, lat in ring:
    x = math.radians(lon) * R
    y = math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)) * R
    px = (x - EXTENT[0]) / (EXTENT[2] - EXTENT[0]) * W
    py = (EXTENT[3] - y) / (EXTENT[3] - EXTENT[1]) * H
    pts.append((px, py))

im = Image.open(PHOTO).convert("RGBA")
overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
d = ImageDraw.Draw(overlay)
d.polygon(pts, fill=(20, 130, 255, 42), outline=(255, 35, 35, 255), width=4)
Image.alpha_composite(im, overlay).convert("RGB").save(OUT, quality=96)
print(OUT)
