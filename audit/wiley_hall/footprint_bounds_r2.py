"""Compare the correct WILY GIS feature with the modeled main-brick-shell bounds."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
query = json.loads((ROOT / "audit/wiley_hall/gis_query.json").read_text(encoding="utf8"))
manifest = json.loads((ROOT / "modular/manifest.json").read_text(encoding="utf8"))
mesh_bounds = json.loads((ROOT / "audit/wiley_hall/mesh_bounds_r2.json").read_text(encoding="utf8"))
matches = [f for f in query["features"] if f.get("properties", {}).get("OBJECTID") == 290
           and f.get("properties", {}).get("ABBR") == "WILY"
           and f.get("properties", {}).get("buildingidlong") == 148]
if len(matches) != 1:
    raise RuntimeError(f"Expected exactly one WILY OBJECTID 290 feature; got {len(matches)}")
feature = matches[0]
ring = feature["geometry"]["coordinates"][0]
lon_m = 111412.84 * math.cos(math.radians(40.4274))
local_ring = [[(lon + 86.9137) * lon_m, (lat - 40.4274) * 111040.0] for lon, lat in ring]
gis_bounds = [[min(p[i] for p in local_ring), max(p[i] for p in local_ring)] for i in range(2)]
area = 0.0
for p, q in zip(local_ring, local_ring[1:] + local_ring[:1]):
    area += p[0] * q[1] - q[0] * p[1]
area = abs(area) * 0.5
record = next(x for x in manifest["assets"] if x["id"] == "wiley_hall")
origin = record["placement_origin_xy_m"]
shell_name = "Wiley | warm russet brick / real-size 230 x 76 mm.001"
shell_vertices_bounds = mesh_bounds[shell_name]
shell_local = [[shell_vertices_bounds[0][axis], shell_vertices_bounds[1][axis]] for axis in range(3)]
shell_world = [[shell_local[i][0] + origin[i], shell_local[i][1] + origin[i]] for i in range(2)]
gis_center = [(b[0] + b[1]) * 0.5 for b in gis_bounds]
shell_center = [(b[0] + b[1]) * 0.5 for b in shell_world]
gis_size = [b[1] - b[0] for b in gis_bounds]
shell_size = [b[1] - b[0] for b in shell_world]
center_delta = [shell_center[i] - gis_center[i] for i in range(2)]
report = {
    "building": "Harvey W. Wiley Residence Hall",
    "feature": {
        "provider": "Purdue campus GIS layer 0",
        "OBJECTID": 290,
        "ABBR": "WILY",
        "buildingidlong": 148,
        "address": feature["properties"]["ADDRESS"],
        "source_crs": "EPSG:3857; query output requested in EPSG:4326 as retained in gis_query.json",
        "converted_local_crs": "project approximate local X-east/Y-north meters; origin lon -86.9137, lat 40.4274; X factor 111412.84*cos(40.4274deg), Y factor 111040.0",
        "ring_vertex_count": len(ring) - (1 if ring[0] == ring[-1] else 0),
        "ring_area_projected_local_m2_approx": area,
        "source_shape_area_m2_epsg3857": feature["properties"]["Shape.STArea()"],
        "bbox_xy_m": gis_bounds,
        "bbox_size_xy_m": gis_size,
        "bbox_center_xy_m": gis_center,
    },
    "model_shell": {
        "mesh_object_used_for_bounds": shell_name,
        "local_bounds_xyz_m": shell_local,
        "placement_origin_xy_m": origin,
        "world_bounds_xy_m": shell_world,
        "bbox_size_xy_m": shell_size,
        "bbox_center_xy_m": shell_center,
        "center_delta_from_gis_bbox_m": center_delta,
    },
    "uncertainty": [
        "The campus map ring is an identity/location source, not a certified surveyed wall line.",
        "This compares bounding boxes of the GIS ring and main brick shell; it is not a full polygon intersection or proof of exact as-built wall perimeter.",
        "Roof, height, exact facade dimension, and master-neighbor alignment are not verified by this comparison.",
    ],
}
out = Path(__file__).with_name("footprint_bounds_r2.json")
out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf8")
print(json.dumps(report, indent=2))
