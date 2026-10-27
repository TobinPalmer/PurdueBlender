"""Fetch and overlay Indiana's current orthophoto at Provenance FID 506."""
import json
import math
import urllib.parse
import urllib.request
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[2]
AUDIT = Path(__file__).resolve().parent
SOURCE = AUDIT / "sources" / "official_purdue_fid506.json"
BASE = "https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_Current_Imagery/ImageServer"
RETRIEVED = "2026-10-26"

feature = json.loads(SOURCE.read_text(encoding="utf-8"))["feature"]
mercator_ring = feature["geometry"]["rings"][0]
to_ll = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)
to_merc = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
ring_merc = [to_merc.transform(*to_ll.transform(x, y)) for x, y in mercator_ring]
xs, ys = zip(*ring_merc)
pad = 38.0
bbox = [min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad]
w, h = 1800, 1050
params = {
    "bbox": ",".join(f"{v:.3f}" for v in bbox),
    "bboxSR": "3857", "imageSR": "3857", "size": f"{w},{h}",
    "format": "jpg", "f": "image", "interpolation": "RSP_BilinearInterpolation",
}
image_url = BASE + "/exportImage?" + urllib.parse.urlencode(params)
raw_bytes = urllib.request.urlopen(image_url, timeout=60).read()
im = Image.open(BytesIO(raw_bytes)).convert("RGB")
if im.size != (w, h):
    raise RuntimeError(f"Unexpected ImageServer dimensions {im.size}")
raw_path = AUDIT / "sources" / "indiana_current_orthophoto_2025_raw.jpg"
im.save(raw_path, quality=96)

draw = ImageDraw.Draw(im)
pts = [((x - bbox[0]) / (bbox[2] - bbox[0]) * w,
        (bbox[3] - y) / (bbox[3] - bbox[1]) * h) for x, y in ring_merc]
draw.line(pts, fill=(255, 28, 20), width=5)
cx = sum(p[0] for p in pts) / len(pts)
cy = sum(p[1] for p in pts) / len(pts)
draw.text((cx, cy), "Purdue GIS FID 506 / Building F / 143", fill=(255, 255, 0),
          stroke_width=2, stroke_fill=(0, 0, 0))
overlay_path = AUDIT / "indiana_current_orthophoto_2025_fid506_overlay.jpg"
im.save(overlay_path, quality=96)

centroid = (sum(x for x, _ in ring_merc) / len(ring_merc),
            sum(y for _, y in ring_merc) / len(ring_merc))
identify_params = {
    "geometry": f"{centroid[0]},{centroid[1]}",
    "geometryType": "esriGeometryPoint", "sr": "3857",
    "returnGeometry": "false", "returnCatalogItems": "true", "f": "json",
}
identify_url = BASE + "/identify?" + urllib.parse.urlencode(identify_params)
catalog = json.loads(urllib.request.urlopen(identify_url, timeout=40).read())
items = [f.get("attributes", {}) for f in catalog.get("catalogItems", {}).get("features", [])]
service_metadata = json.loads(urllib.request.urlopen(BASE + "?f=pjson", timeout=40).read())
metadata_path = AUDIT / "sources" / "indiana_current_orthophoto_layer_metadata.json"
metadata_path.write_text(json.dumps(service_metadata, indent=2) + "\n", encoding="utf-8")
record = {
    "provider": "Indiana Geographic Information Office / Indiana Current Orthophotography ImageServer",
    "service_url": BASE,
    "imagery_dataset": "Indiana_2025_SPW_2ft_exportraster, confirmed by ImageServer identify at the FID 506 centroid; ImageServer catalog also reports in2023_29921882_06 and Indiana_2023_SPW_06in.",
    "retrieved": RETRIEVED,
    "source_date": "2025 imagery catalog item (Indiana_2025_SPW_2ft_exportraster); 2023 items are also returned. Tile-level flight date was not exposed by identify.",
    "license": "Indiana GIS metadata states CC0 for statewide orthophotography.",
    "service_metadata_snapshot": metadata_path.relative_to(ROOT).as_posix(),
    "source_feature": {
        "provider": "Purdue University Campus Map FeatureServer, BuildingShapesZip4 layer 0",
        "feature_id": 506,
        "name": "Building F", "abbreviation": "143",
        "layer": "BLDG Building Pre-planning",
        "source_snapshot": "sources/official_purdue_fid506.json",
        "polygon_crs": "EPSG:3857",
    },
    "request_bbox_epsg3857": bbox,
    "image_px": [w, h],
    "raw_image": raw_path.relative_to(ROOT).as_posix(),
    "overlay_image": overlay_path.relative_to(ROOT).as_posix(),
    "catalog_items_at_centroid": items,
    "overlay_method": "The Purdue polygon is inverse-projected from EPSG:3857 to WGS84 then projected to EPSG:3857; it is drawn over the current orthophoto in the same EPSG:3857 request envelope. No image rescaling/warping beyond service export is applied.",
    "limitations": [
        "The Purdue polygon is explicitly tagged pre-planning; an overlay over current orthophoto tests registration and outline similarity but does not by itself prove the source polygon is an as-built wall line.",
        "Orthophoto confirms roof plan position/shape and current construction presence, not wall heights, elevations, entries, or facade openings.",
        "The project-local coordinate conversion used elsewhere in the model is approximate, not surveyed geodetic control.",
    ],
}
(AUDIT / "indiana_current_orthophoto_2025_registration.json").write_text(
    json.dumps(record, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"raw_image": str(raw_path), "overlay": str(overlay_path),
                  "image_bytes": len(raw_bytes), "bbox": bbox,
                  "catalog_items": items}, indent=2))
