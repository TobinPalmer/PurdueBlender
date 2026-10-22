"""Refresh one manifest record after localizing its source library."""
import bpy
import json
import sys
from pathlib import Path
from mathutils import Vector

MODULAR = Path(__file__).resolve().parent
path = MODULAR / "manifest.json"
manifest = json.loads(path.read_text(encoding="utf-8"))
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if len(args) != 1:
    raise RuntimeError("Expected one building ID after --")
asset_id = args[0]
record = next(a for a in manifest["assets"] if a["id"] == asset_id)
collection = bpy.data.collections.get(record["collection"])
if collection is None:
    raise RuntimeError(f"Missing collection {record['collection']}")
anchor = tuple(collection.get("placement_origin_xy_m", (None, None)))
if None in anchor:
    raise RuntimeError(f"Missing placement origin for {asset_id}")
objects = list(collection.all_objects)
geometry = [o for o in objects if o.type in {"MESH", "CURVE", "FONT", "SURFACE", "META"}]
points = [o.matrix_world @ Vector(corner) for o in geometry for corner in o.bound_box]
local_bounds = [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]
world_bounds = [
    [local_bounds[0][0] + anchor[0], local_bounds[0][1] + anchor[0]],
    [local_bounds[1][0] + anchor[1], local_bounds[1][1] + anchor[1]],
    local_bounds[2],
]
record.update({
    "objects": [o.name for o in objects],
    "object_count": len(objects),
    "bounds_world_m": world_bounds,
    "source_bounds_world_m": world_bounds,
    "local_bounds_m": local_bounds,
    "placement_origin_xy_m": [anchor[0], anchor[1]],
    "local_coordinates": True,
    "placement_transform": "master collection-instance marker translates local geometry to placement_origin_xy_m",
})
path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(json.dumps({"id": asset_id, "objects": len(objects), "origin": anchor, "bounds": world_bounds}))
