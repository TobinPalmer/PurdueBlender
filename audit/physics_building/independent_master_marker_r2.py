import bpy
import json
from pathlib import Path
from math import dist

ROOT = Path(__file__).resolve().parents[2]
MASTER = ROOT / "purdue_campus_master.blend"
OUT = Path(__file__).resolve().parent / "independent_master_marker_r2.json"
asset_id = "physics_building"
collection_name = "Asset_physics_building"
marker_name = "Placement_physics_building"
asset_path = (ROOT / "modular/buildings/physics_building_phys_3bf42f3.blend").resolve()
bpy.ops.wm.open_mainfile(filepath=str(MASTER))
scene = bpy.context.scene
marker = bpy.data.objects.get(marker_name)
collection = bpy.data.collections.get(collection_name)
if marker is None or collection is None:
    raise RuntimeError("Physics Building placement marker or linked collection missing in master")
library_path = Path(bpy.path.abspath(collection.library.filepath)).resolve() if collection.library else None
record = json.loads((ROOT / "modular/manifest.json").read_text(encoding="utf-8"))
record = next(a for a in record["assets"] if a["id"] == asset_id)
expected = [float(v) for v in record["placement_origin_xy_m"]]
actual = [float(marker.location.x), float(marker.location.y)]
out = {
    "master": str(MASTER),
    "master_opened_without_saving": True,
    "marker": marker.name,
    "marker_xy_m": actual,
    "marker_z_m": float(marker.location.z),
    "manifest_xy_m": expected,
    "placement_error_m": dist(actual, expected),
    "scale": list(marker.scale),
    "rotation_euler": list(marker.rotation_euler),
    "instance_collection": marker.instance_collection.name if marker.instance_collection else None,
    "linked_collection": collection.name,
    "linked_objects_on_master_reopen": len(collection.all_objects),
    "linked_library_path": str(library_path) if library_path else None,
    "expected_library_path": str(asset_path),
    "root_direct_collection_link": any(child.name == collection_name for child in scene.collection.children),
}
out["marker_matches_manifest"] = out["placement_error_m"] <= 0.001 and abs(out["marker_z_m"]) <= 0.001
out["library_path_matches_asset"] = library_path == asset_path
out["marker_instances_linked_collection"] = marker.instance_collection == collection
OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(out, indent=2, ensure_ascii=False))
