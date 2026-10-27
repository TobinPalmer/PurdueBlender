"""Recompute the AOII slab footprint against OSM way/970455277."""
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path

from shapely.geometry import Polygon

ROOT = Path(__file__).resolve().parents[3]
OSM_PATH = ROOT / "audit" / "alpha_omicron_pi" / "osm_way_970455277.xml"
PROBE_PATH = Path(__file__).with_name("fresh_open_probe.json")
REGISTER_PATH = ROOT / "audit" / "alpha_omicron_pi" / "source_register.json"

register = json.loads(REGISTER_PATH.read_text(encoding="utf-8"))
origin = register["model"].get("placement_origin_world_xy_m", register["model"].get("origin_world_xy_m"))
probe = json.loads(PROBE_PATH.read_text(encoding="utf-8"))
if probe["errors"]:
    raise RuntimeError(f"Fresh-open probe errors: {probe['errors']}")

tree = ET.parse(OSM_PATH)
osm = tree.getroot()
nodes = {n.attrib["id"]: (float(n.attrib["lon"]), float(n.attrib["lat"]))
         for n in osm.findall("node")}
way = next(w for w in osm.findall("way") if w.attrib.get("id") == "970455277")
refs = [nd.attrib["ref"] for nd in way.findall("nd")]
source_xy = []
for ref in refs:
    lon, lat = nodes[ref]
    x = (lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274))
    y = (lat - 40.4274) * 111040.0
    source_xy.append((x - origin[0], y - origin[1]))
if source_xy and source_xy[0] == source_xy[-1]:
    source_xy.pop()
model_xy = [tuple(p) for p in probe["slab_ring_xy_local_m"]]
source_poly = Polygon(source_xy)
model_poly = Polygon(model_xy)
intersection_area = source_poly.intersection(model_poly).area
union_area = source_poly.union(model_poly).area
result = {
    "source": "OSM way 970455277, raw WGS84 nodes in audit/alpha_omicron_pi/osm_way_970455277.xml",
    "asset_sha256": probe["sha256"],
    "feature_id": "way/970455277",
    "coordinate_method": "Project approximate campus XY formula; subtract recorded origin_world_xy_m",
    "asset_geometry": "Fresh-open AOII_Level_1_Slab lowest-z ring",
    "source_vertex_count": len(source_xy),
    "model_vertex_count": len(model_xy),
    "source_area_m2": source_poly.area,
    "model_area_m2": model_poly.area,
    "iou": intersection_area / union_area if union_area else None,
    "symmetric_hausdorff_m": max(source_poly.hausdorff_distance(model_poly), model_poly.hausdorff_distance(source_poly)),
    "centroid_delta_m": [model_poly.centroid.x - source_poly.centroid.x, model_poly.centroid.y - source_poly.centroid.y],
    "source_bounds_local_m": list(source_poly.bounds),
    "model_bounds_local_m": list(model_poly.bounds),
    "limitation": "The massing was originally created from this OSM polygon; this is a transform/serialization recheck, not independent proof of the structural wall line or parcel identity.",
}
Path(__file__).with_name("gis_comparison.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
