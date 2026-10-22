"""Convert one detailed building library to local coordinates for master placement.

Run inside Blender with: --python localize_building_asset.py -- <building_id>
The matching source file is updated in place; callers should make a backup first.
"""
import bpy
import json
import sys
from pathlib import Path
from mathutils import Vector

MODULAR = Path(__file__).resolve().parent
manifest = json.loads((MODULAR / "manifest.json").read_text(encoding="utf-8"))
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if len(args) != 1:
    raise RuntimeError("Expected one building ID after --")
asset_id = args[0]
record = next((a for a in manifest["assets"] if a["id"] == asset_id), None)
if record is None:
    raise RuntimeError(f"Unknown asset ID: {asset_id}")
if record.get("local_coordinates"):
    print(f"ALREADY_LOCAL {asset_id}")
    raise SystemExit(0)

collection = bpy.data.collections.get(record["collection"])
if collection is None:
    raise RuntimeError(f"Missing exported collection {record['collection']}")
objects = list(collection.all_objects)
geometry = [o for o in objects if o.type in {"MESH", "CURVE", "FONT", "SURFACE", "META"}]
points = [o.matrix_world @ Vector(corner) for o in geometry for corner in o.bound_box]
if not points:
    raise RuntimeError(f"No bounded geometry in {record['collection']}")
bounds = [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]
anchor = ((bounds[0][0] + bounds[0][1]) * 0.5,
          (bounds[1][0] + bounds[1][1]) * 0.5,
          0.0)

# Parent only collection roots, preserving any existing building hierarchy.
members = set(objects)
roots = [o for o in objects if o.parent not in members]
root = bpy.data.objects.new(f"AssetRoot_{asset_id}", None)
root.empty_display_type = "PLAIN_AXES"
root.empty_display_size = 2.0
collection.objects.link(root)
root.location = anchor
bpy.context.view_layer.update()
for obj in roots:
    world = obj.matrix_world.copy()
    obj.parent = root
    obj.matrix_parent_inverse = root.matrix_world.inverted()
    obj.matrix_world = world
bpy.context.view_layer.update()

# Moving this root to the local origin converts all child coordinates by -anchor.
root.location = (0.0, 0.0, 0.0)
bpy.context.view_layer.update()
collection["placement_origin_xy_m"] = [anchor[0], anchor[1]]
collection["coordinate_frame"] = "local; master placement marker supplies XY origin"
scene = bpy.data.scenes.get(record.get("scene", ""))
if scene is not None:
    scene["placement_origin_xy_m"] = [anchor[0], anchor[1]]
    scene["coordinate_frame"] = "local; master placement marker supplies XY origin"

bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print(json.dumps({"status": "LOCALIZED", "id": asset_id, "anchor": anchor,
                  "world_bounds_before": bounds, "collection_objects": len(objects),
                  "root_objects": len(roots)}))
