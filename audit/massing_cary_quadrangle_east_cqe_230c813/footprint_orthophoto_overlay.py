"""Draw the official CQE footprint against the Indiana 2023 orthophoto crop."""
import json
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "audit" / "massing_cary_quadrangle_east_cqe_230c813"
SOURCES = EVIDENCE / "sources"
meta = json.loads((SOURCES / "indiana_2023_orthophoto_metadata.json").read_text(encoding="utf-8-sig"))
crop = json.loads((SOURCES / "purdue_building_shapes_fid639_cqe_2026-10-25.geojson").read_text(encoding="utf-8-sig"))
image = Image.open(SOURCES / "indiana_2023_orthophoto_cqe.jpg").convert("RGB")
extent = meta["extent_wgs84"]
xmin, ymin, xmax, ymax = extent
width, height = image.size

def xy(lon, lat):
    return ((lon-xmin)/(xmax-xmin)*width, (ymax-lat)/(ymax-ymin)*height)

ring = crop["features"][0]["geometry"]["coordinates"][0]
points = [xy(lon, lat) for lon, lat in ring]
draw = ImageDraw.Draw(image)
draw.line(points, fill=(255, 30, 40), width=5)
draw.text((12, 16), "Purdue GIS CQE FID 639 footprint on Indiana 2023 orthophoto", fill="yellow", stroke_width=2, stroke_fill="black")
out = EVIDENCE / "cqe_orthophoto_footprint_overlay.png"
image.save(out)
print(out)
