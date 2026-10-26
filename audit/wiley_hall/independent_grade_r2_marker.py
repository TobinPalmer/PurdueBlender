import json
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[2]
MASTER = ROOT / "purdue_campus_master.blend"
OUT = Path(__file__).with_name("independent_grade_r2_marker.json")
bpy.ops.wm.open_mainfile(filepath=str(MASTER))
marker = bpy.data.objects.get("Placement_wiley_hall")
if marker is None:
    raise RuntimeError("Placement_wiley_hall not found in master")
collection = marker.instance_collection
record = {
    "master": str(MASTER),
    "read_only_reopen": True,
    "marker": marker.name,
    "location_m": list(marker.location),
    "rotation_euler_rad": list(marker.rotation_euler),
    "scale": list(marker.scale),
    "instance_collection": collection.name if collection else None,
    "library_path": bpy.path.abspath(collection.library.filepath) if collection and collection.library else None,
    "marker_matrix_world": [list(row) for row in marker.matrix_world],
}
OUT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
print(json.dumps(record, indent=2))
