"""Move oversized master-owned context out of Wiley's exported building collection."""
import hashlib
import json
from pathlib import Path

import bpy


ASSET = Path(bpy.data.filepath).resolve()
EXPECTED = Path(__file__).resolve().parents[2] / "modular/buildings/wiley_hall.blend"
if ASSET != EXPECTED.resolve():
    raise RuntimeError(f"Unexpected asset file: {ASSET}")
export = bpy.data.collections.get("Asset_wiley_hall")
if export is None:
    raise RuntimeError("Missing stable export collection Asset_wiley_hall")
scene = bpy.context.scene
exclude_names = {
    "Lawn | mixed summer grass.001",
    "Road | aged asphalt.001",
    "Road | faded yellow.001",
    "Road | parking paint.001",
}
excluded = [bpy.data.objects.get(name) for name in sorted(exclude_names)]
if any(obj is None for obj in excluded):
    raise RuntimeError("One or more expected site-context objects were not found")
site_context = bpy.data.collections.get("Wiley_SiteContext_NotExported")
if site_context is None:
    site_context = bpy.data.collections.new("Wiley_SiteContext_NotExported")
    scene.collection.children.link(site_context)
site_context.hide_render = True
site_context.hide_viewport = True

def matrix_rows(matrix):
    return [[float(v) for v in row] for row in matrix]

before = {}
for obj in excluded:
    if export not in obj.users_collection:
        raise RuntimeError(f"{obj.name} is not directly in the building export collection")
    before[obj.name] = {
        "matrix_world": matrix_rows(obj.matrix_world),
        "parent": obj.parent.name if obj.parent else None,
        "dimensions": [float(v) for v in obj.dimensions],
        "bounds_local": [[float(v) for v in obj.bound_box[0]], [float(v) for v in obj.bound_box[6]]],
    }
    obj.users_collection[0].objects.unlink(obj)
    site_context.objects.link(obj)

for obj in excluded:
    if matrix_rows(obj.matrix_world) != before[obj.name]["matrix_world"]:
        raise RuntimeError(f"Moving {obj.name} changed its world transform")
    if export in obj.users_collection or site_context not in obj.users_collection:
        raise RuntimeError(f"{obj.name} was not cleanly separated from the building export")

bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
report = {
    "asset": str(ASSET),
    "sha256": hashlib.sha256(ASSET.read_bytes()).hexdigest(),
    "export_collection": export.name,
    "export_object_count": len(export.all_objects),
    "excluded_context_collection": site_context.name,
    "excluded_context_hidden_in_source_scene": True,
    "objects_moved_without_transform_or_parent_changes": before,
    "reason": "The 680x660m rectangular lawn and broad road/marking surfaces are generic master-level context, not verified Wiley Hall shell geometry; keeping them outside Asset_wiley_hall prevents campus-wide overlap while preserving the source geometry for inspection.",
}
out = Path(__file__).with_name("site_context_separation_r2.json")
out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf8")
print(json.dumps(report, indent=2))
