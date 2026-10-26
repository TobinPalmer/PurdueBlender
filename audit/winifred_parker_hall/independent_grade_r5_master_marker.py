"""Read-only fresh-process master placement and library check for Winifred R5."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[2]
MASTER = ROOT / "purdue_campus_master.blend"
ASSET = ROOT / "modular/buildings/winifred_parker_hall.blend"
OUT = Path(__file__).resolve().parent / "independent_grade_r5_master_marker.json"
EXPECTED_SHA = "92fa120794470d93a253d04f35ca0852caea7d05982a5f4e02b285fd914045a9"
if Path(bpy.data.filepath).resolve() != MASTER.resolve():
    raise RuntimeError("Must freshly open the current master in read-only mode")
sha = hashlib.sha256(ASSET.read_bytes()).hexdigest()
if sha != EXPECTED_SHA:
    raise RuntimeError(f"Canonical asset SHA changed during grading: {sha}")
manifest = json.loads((ROOT / "modular/manifest.json").read_text(encoding="utf-8"))
record = next((r for r in manifest["assets"] if r["id"] == "winifred_parker_hall"), None)
if record is None:
    raise RuntimeError("Winifred is missing from the master manifest")
marker = bpy.data.objects.get("Placement_winifred_parker_hall")
collection = bpy.data.collections.get("Asset_winifred_parker_hall")
if marker is None or collection is None or marker.instance_collection != collection:
    raise RuntimeError("Expected Winifred marker is absent or instances the wrong collection")
library_path = Path(bpy.path.abspath(collection.library.filepath)).resolve()
if library_path != ASSET.resolve():
    raise RuntimeError(f"Winifred linked library resolves to {library_path}, not {ASSET}")
if len(collection.all_objects) != 582:
    raise RuntimeError(f"Linked object count is {len(collection.all_objects)}, expected 582")
origin = record.get("placement_origin_xy_m")
if not origin or len(origin) != 2:
    raise RuntimeError("Winifred manifest placement origin is missing")
error = ((float(marker.location.x) - float(origin[0])) ** 2 +
         (float(marker.location.y) - float(origin[1])) ** 2) ** 0.5
if error > 0.001 or abs(float(marker.location.z)) > 0.001:
    raise RuntimeError(f"Winifred marker error is {error:.6f} m")
if any(abs(float(value) - 1.0) > 1e-6 for value in marker.scale):
    raise RuntimeError("Winifred marker scale is not identity")
if any(abs(float(value)) > 1e-6 for value in marker.rotation_euler):
    raise RuntimeError("Winifred marker rotation is not identity")
directly_linked = any(child.name == collection.name for child in bpy.context.scene.collection.children)
if directly_linked:
    raise RuntimeError("Winifred source collection is directly linked in addition to its placement marker")
report = {
    "fresh_process_read_only_master_reopen": True,
    "master": str(MASTER),
    "asset_sha256": sha,
    "expected_asset_sha256": EXPECTED_SHA,
    "marker": marker.name,
    "marker_instance_collection": collection.name,
    "source_library": str(library_path),
    "source_library_matches_asset": True,
    "linked_object_count": len(collection.all_objects),
    "marker_xyz": [float(marker.location.x), float(marker.location.y), float(marker.location.z)],
    "manifest_origin_xy_m": [float(origin[0]), float(origin[1])],
    "marker_position_error_m": error,
    "rotation_euler": [float(v) for v in marker.rotation_euler],
    "scale": [float(v) for v in marker.scale],
    "direct_source_collection_also_linked": directly_linked,
}
OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2, ensure_ascii=False))
