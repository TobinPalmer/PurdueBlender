import hashlib, json, re
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular/buildings/university_hall.blend"
EXPECTED_SHA256 = "7ed748bb216108115986f276cb5558a445559be75245be95639158221d8538c1"
actual = hashlib.sha256(ASSET.read_bytes()).hexdigest()
if actual != EXPECTED_SHA256:
    raise RuntimeError(f"Frozen R7 SHA mismatch: {actual}")
if Path(bpy.data.filepath).resolve() != ASSET.resolve():
    raise RuntimeError(f"Wrong Blender file open: {bpy.data.filepath}")

collection = bpy.data.collections.get("Asset_university_hall")
if collection is None:
    raise RuntimeError("Asset_university_hall is missing")
names = sorted(o.name for o in collection.all_objects)
patterns = {
    "stair_flights": "StairFlight",
    "gallery_landings": "StairLanding",
    "gallery_floor_meshes": "GalleryFloor",
    "reclaimed_display_columns": "UNIV_R5_ReclaimedDisplayColumn_",
    "window_hoods": "UNIV_R7_Window_",
    "entry_details": "UNIV_R7_Entry_",
    "portico_details": "UNIV_R7_Portico_",
}
groups = {key: [name for name in names if token in name] for key, token in patterns.items()}
column_roots = sorted({re.sub(r"_(Capital|Flute_\d+|Foot|LowerMould|Neck|Shaft)$", "", name)
                       for name in groups["reclaimed_display_columns"]})
rows = []
deps = bpy.context.evaluated_depsgraph_get()
for obj in collection.all_objects:
    if obj.type != "MESH" or not any(token in obj.name for token in ("StairFlight", "StairLanding", "GalleryFloor", "ReclaimedDisplayColumn")):
        continue
    evaluated = obj.evaluated_get(deps)
    mesh = evaluated.to_mesh()
    try:
        points = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
        if not points:
            continue
        bounds = [[min(float(p[i]) for p in points), max(float(p[i]) for p in points)] for i in range(3)]
    finally:
        evaluated.to_mesh_clear()
    rows.append({"name": obj.name, "bounds_m": bounds, "parent": obj.parent.name if obj.parent else None})

root = bpy.data.objects.get("AssetRoot_university_hall")
report = {
    "asset": str(ASSET),
    "sha256": actual,
    "blender_version": bpy.app.version_string,
    "fresh_exact_file_reopen": True,
    "export_collection": collection.name,
    "export_object_count": len(collection.all_objects),
    "root_transform": {
        "location": list(root.location) if root else None,
        "rotation_euler": list(root.rotation_euler) if root else None,
        "scale": list(root.scale) if root else None,
    },
    "named_geometry_counts": {key: len(value) for key, value in groups.items()},
    "reclaimed_display_column_assembly_roots": column_roots,
    "empty_mesh_objects": [o.name for o in collection.all_objects if o.type == "MESH" and len(o.data.vertices) == 0],
    "named_geometry_objects": groups,
    "evaluated_saved_gallery_and_column_bounds": rows,
}
OUT = ROOT / "audit/university_hall_refine/independent_grade_r7_structure.json"
OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
