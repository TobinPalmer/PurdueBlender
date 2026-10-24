"""Read-only reopen and source-footprint validation for Math Sciences."""

import bpy
import json
import math
import mathutils
from pathlib import Path

ROOT = Path(r"C:/Users/Tobin/Documents/Blender/PurdueMap")
ASSET = ROOT / "modular/buildings/math_sciences.blend"
MANIFEST = ROOT / "modular/manifest.json"
GIS = ROOT / "audit/batch3_math/gis_fid227.geojson"
OUT = ROOT / "audit/batch3_math/round7_validation.json"

# The script is invoked against Blender, then opens only the standalone building.
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
entry = next(x for x in manifest["assets"] if x["id"] == "math_sciences")
asset = bpy.data.collections.get(entry["collection"])
shell = bpy.data.objects.get("MATH_Corrected_GIS_Wall_Envelope")
if asset is None or shell is None or shell.type != "MESH":
    raise RuntimeError("Expected Math Sciences asset collection or GIS envelope is missing")

origin = entry["placement_origin_xy_m"]
verts = shell.data.vertices
shell_bounds = [
    [min(v.co[i] for v in verts), max(v.co[i] for v in verts)]
    for i in range(3)
]
feature = json.loads(GIS.read_text(encoding="utf-8"))["features"][0]
ring = feature["geometry"]["coordinates"][0]
projected = [
    [
        (lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)) - origin[0],
        (lat - 40.4274) * 111040.0 - origin[1],
    ]
    for lon, lat in ring
]
source_bounds = [
    [min(p[i] for p in projected), max(p[i] for p in projected)]
    for i in range(2)
]
bound_deltas = [
    [shell_bounds[i][j] - source_bounds[i][j] for j in range(2)]
    for i in range(2)
]
all_objects = list(asset.all_objects)
result = {
    "date": "2026-10-24",
    "asset": str(ASSET.relative_to(ROOT)).replace("\\", "/"),
    "opened_saved_asset": True,
    "stable_id": entry["id"],
    "export_collection": entry["collection"],
    "manifest_origin_xy_m": origin,
    "direct_objects": len(asset.objects),
    "all_export_objects": len(all_objects),
    "shell_object": shell.name,
    "shell_local_bounds_m": shell_bounds,
    "gis_feature_id": feature["id"],
    "gis_crs": "EPSG:4326; transformed using project approximation documented in modular/AGENTS.md",
    "gis_local_bounds_m": source_bounds,
    "shell_minus_gis_bbox_edges_m": bound_deltas,
    "max_absolute_bbox_edge_delta_m": max(abs(v) for row in bound_deltas for v in row),
    "east_sign_absent": bpy.data.objects.get("MATH_Signage_East") is None,
    "height": {
        "documented_story_count": 10,
        "supported_by": "Purdue Archives and Special Collections record",
        "model_wall_top_estimate_m": shell_bounds[2][1],
        "model_max_with_mast_estimate_m": max(
            (o.matrix_world @ mathutils.Vector(corner)).z
            for o in all_objects
            if o.type == "MESH"
            for corner in o.bound_box
        ),
        "warning": "Metric height, floor spacing, roof/penthouse profile and mast height remain estimated; GIS elevation-like fields have no published unit/field definitions.",
    },
    "source_review": {
        "purdue_archives_10_story_identity": "https://archives.lib.purdue.edu/agents/corporate_entities/672",
        "purdue_statistics_exterior_photo": "https://www.stat.purdue.edu/images/about/Math-Bldg-.jpg",
        "google_maps_pin_street_view": "https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=40.4261348,-86.915642",
        "google_maps_result": "No Street View imagery available at that pin in the 2026-10-24 check.",
        "photo_supported_features": [
            "light red brick",
            "pale vertical window surrounds",
            "repeated narrow window bays",
            "a large opening below the upper building mass",
        ],
        "photo_limit": "The low-resolution image is not georeferenced and does not identify which model elevation it shows, so it cannot justify adding a facade pattern to a specific wall.",
    },
    "status": "Reopen and plan-envelope verification only; this validation does not claim roof, facade schedule, interior or height accuracy.",
}
OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
