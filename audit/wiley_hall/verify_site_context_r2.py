"""Fresh-process validation of the optional site-context separation."""
import hashlib
import json
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
ASSET = Path(bpy.data.filepath).resolve()
expected = json.loads((HERE / "site_context_separation_r2.json").read_text(encoding="utf8"))
if ASSET != Path(expected["asset"]).resolve():
    raise RuntimeError("Opened a different asset than the R2 separation record")
digest = hashlib.sha256(ASSET.read_bytes()).hexdigest()
if digest != expected["sha256"]:
    raise RuntimeError(f"Asset SHA mismatch: {digest}")
export = bpy.data.collections.get("Asset_wiley_hall")
site = bpy.data.collections.get("Wiley_SiteContext_NotExported")
if export is None or site is None:
    raise RuntimeError("Missing stable building export or separated site-context collection")
if len(export.all_objects) != expected["export_object_count"]:
    raise RuntimeError("Export collection object count differs from the saved separation record")
if not site.hide_render or not site.hide_viewport:
    raise RuntimeError("Separated site context is not hidden in the source scene")
if len(site.all_objects) != 4:
    raise RuntimeError(f"Site context has {len(site.all_objects)} objects; expected 4")
checks = []
site.hide_viewport = False
bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()
for name, before in expected["objects_moved_without_transform_or_parent_changes"].items():
    obj = bpy.data.objects.get(name)
    if obj is None or site.objects.get(name) is not obj or export.objects.get(name) is not None:
        raise RuntimeError(f"{name} is not isolated from the exported building")
    if (obj.parent.name if obj.parent else None) != before["parent"]:
        raise RuntimeError(f"{name} parent changed")
    evaluated = obj.evaluated_get(depsgraph)
    actual = [[float(v) for v in row] for row in evaluated.matrix_world]
    delta = max(abs(actual[i][j] - before["matrix_world"][i][j]) for i in range(4) for j in range(4))
    if delta > 1e-4:
        raise RuntimeError(f"{name} transform changed during separation: delta={delta}; expected={before['matrix_world']}; actual={actual}")
    checks.append({"name": name, "matrix_world_unchanged_within_0.1mm": True,
                   "matrix_max_abs_rounding_delta_m": delta, "exported": False})
site.hide_viewport = True
bpy.context.view_layer.update()
report = {
    "asset": str(ASSET),
    "sha256": digest,
    "fresh_reopen": True,
    "export_collection": export.name,
    "export_object_count": len(export.all_objects),
    "site_context_collection": site.name,
    "site_context_object_count": len(site.all_objects),
    "hidden_in_source_scene": True,
    "matrix_parent_and_membership_checks": checks,
    "root_identity": {
        "location": list(bpy.data.objects["AssetRoot_wiley_hall"].location),
        "rotation": list(bpy.data.objects["AssetRoot_wiley_hall"].rotation_euler),
        "scale": list(bpy.data.objects["AssetRoot_wiley_hall"].scale),
    },
}
(HERE / "site_context_reopen_r2.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf8")
print(json.dumps(report, indent=2))
