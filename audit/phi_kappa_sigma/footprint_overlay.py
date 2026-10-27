"""Project the official FID 829 ring onto the archived Esri World Imagery tiles."""
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "audit" / "phi_kappa_sigma" / "sources"
z, x0, y0 = 20, 271163, 395344
im = Image.open(SRC / "esri_world_imagery_detail_2026-10-26.png").convert("RGB")
feature = json.loads((SRC / "purdue_gis_fid829_2026-10-26.json").read_text(encoding="utf-8"))["features"][0]
n = 2 ** z
points = []
for lon, lat in feature["geometry"]["rings"][0]:
    px = (lon + 180.0) / 360.0 * n * 256 - x0 * 256
    py = (1.0 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * n * 256 - y0 * 256
    points.append((px, py))
draw = ImageDraw.Draw(im, "RGBA")
draw.polygon(points, fill=(255, 30, 20, 50), outline=(255, 25, 20, 255), width=3)
draw.text((8, 8), "Purdue GIS BuildingShapesZip4 FID 829 over Esri World Imagery", fill=(255, 255, 0, 255))
im.save(SRC / "fid829_footprint_overlay.png")
print("Overlay saved; ring points:", len(points))
