"""Fresh-open verification for detailed libraries linked in the campus master."""
import bpy
import hashlib
import json
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
MODULAR = ROOT / "modular"
manifest = json.loads((MODULAR / "manifest.json").read_text(encoding="utf-8"))
verification = json.loads((MODULAR / "verification.json").read_text(encoding="utf-8"))
scene = bpy.context.scene
root_collection = scene.collection
details = [a for a in manifest["assets"] if a.get("kind") == "detailed"]
expected_markers = {f"Placement_{a['id']}" for a in details}
actual_markers = {o.name for o in scene.objects if o.name.startswith("Placement_")}
errors = []
records = {}


def local_matrix(obj, cache):
    if obj in cache:
        return cache[obj]
    matrix = obj.matrix_local.copy()
    if obj.parent is not None:
        matrix = local_matrix(obj.parent, cache) @ matrix
    cache[obj] = matrix
    return matrix


if verification.get("status") != "PASS":
    errors.append(f"saved modular verification is {verification.get('status')}")
if actual_markers != expected_markers:
    errors.append(
        f"marker set mismatch; missing={sorted(expected_markers-actual_markers)}, "
        f"extra={sorted(actual_markers-expected_markers)}"
    )

for asset in details:
    aid = asset["id"]
    marker_name = f"Placement_{aid}"
    marker = bpy.data.objects.get(marker_name)
    if marker is None:
        continue
    col = marker.instance_collection
    if marker.instance_type != "COLLECTION" or col is None:
        errors.append(f"{aid}: marker is not a linked collection instance")
        continue
    expected_file = (MODULAR / asset["file"]).resolve()
    library_file = Path(bpy.path.abspath(col.library.filepath)).resolve() if col.library else None
    if library_file != expected_file:
        errors.append(f"{aid}: linked library mismatch {library_file} != {expected_file}")
    if col in list(root_collection.children):
        errors.append(f"{aid}: detailed library is also directly linked at the master root")
    origin = asset["placement_origin_xy_m"]
    marker_error = max(abs(float(marker.location[i])-float(origin[i])) for i in range(2))
    if marker_error > 0.001:
        errors.append(f"{aid}: marker offset differs from manifest by {marker_error:.6f} m")
    if any(abs(float(v)) > 1e-7 for v in marker.rotation_euler) or any(abs(float(v)-1.0)>1e-7 for v in marker.scale):
        errors.append(f"{aid}: marker rotation or scale is not identity")
    objects = list(col.all_objects)
    if len(objects) != asset.get("object_count"):
        errors.append(f"{aid}: source object count {len(objects)} != manifest {asset.get('object_count')}")
    cache = {}
    pts = [local_matrix(obj, cache) @ Vector(corner)
           for obj in objects if obj.type in {"MESH", "CURVE", "FONT"}
           for corner in obj.bound_box]
    if not pts:
        errors.append(f"{aid}: no geometric objects in linked collection")
        continue
    local = [[min(p[i] for p in pts), max(p[i] for p in pts)] for i in range(3)]
    world = [[local[i][j] + (float(origin[i]) if i < 2 else 0.0) for j in range(2)] for i in range(3)]
    expected_world = asset.get("bounds_world_m")
    bounds_error = max(abs(world[i][j]-expected_world[i][j]) for i in range(3) for j in range(2))
    if bounds_error > 0.01:
        errors.append(f"{aid}: reconstructed campus bounds differ by {bounds_error:.6f} m")
    asset_path = MODULAR / asset["file"]
    records[aid] = {
        "marker": marker_name,
        "library_path": str(library_file),
        "placement_origin_xy_m": list(marker.location[:2]),
        "source_object_count": len(objects),
        "local_bounds_m": local,
        "reconstructed_world_bounds_m": world,
        "manifest_world_bounds_m": expected_world,
        "max_bounds_error_m": bounds_error,
        "asset_sha256": hashlib.sha256(asset_path.read_bytes()).hexdigest(),
    }

assets_by_id = {a["id"]: a for a in manifest["assets"]}
root_child_names = {c.name for c in root_collection.children}
for excluded in manifest.get("excluded_assets", []):
    if excluded["collection"] in root_child_names:
        errors.append(f"excluded collection is linked directly in the master: {excluded['id']}")
for superseded_id in verification.get("superseded_massing_assets", []):
    superseded_asset = assets_by_id.get(superseded_id)
    if superseded_asset and superseded_asset["collection"] in root_child_names:
        errors.append(f"superseded collection is directly linked: {superseded_id}")

report = {
    "status": "PASS" if not errors else "FAIL",
    "fresh_open": True,
    "master_file": str(Path(bpy.data.filepath).resolve()),
    "blender_version": bpy.app.version_string,
    "asset_count": len(manifest["assets"]),
    "detailed_asset_count": len(details),
    "expected_marker_count": len(expected_markers),
    "actual_marker_count": len(actual_markers),
    "verified_assets": records,
    "errors": errors,
}
out = ROOT / "audit" / "master_integration" / "fresh_open_master_2026-10-26.json"
out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report))
if errors:
    raise RuntimeError("Fresh-open master integration validation failed")
