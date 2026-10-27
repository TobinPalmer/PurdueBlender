import bpy
import hashlib
import json
from pathlib import Path
from mathutils import Vector

root = Path(bpy.data.filepath).resolve().parents[2]
asset = Path(bpy.data.filepath).resolve()
collection = bpy.data.collections.get("Asset_massing_house_301840865_cbf7de2")
scene = bpy.context.scene
objects = list(collection.all_objects) if collection else []
mesh_objs = [obj for obj in objects if obj.type == "MESH"]
points = [obj.matrix_world @ Vector(corner) for obj in mesh_objs for corner in obj.bound_box]
bounds = [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)] if points else None
libraries = sorted({bpy.path.abspath(lib.filepath) for lib in bpy.data.libraries})
external_images = []
for image in bpy.data.images:
    if image.source == "FILE" and image.filepath and not image.packed_file:
        p = Path(bpy.path.abspath(image.filepath))
        if not p.exists():
            external_images.append(str(p))
materials = sorted({slot.material.name for obj in mesh_objs for slot in obj.material_slots if slot.material})
report = {
    "asset": str(asset),
    "sha256": hashlib.sha256(asset.read_bytes()).hexdigest(),
    "blender_version": bpy.app.version_string,
    "scene": scene.name,
    "asset_id": scene.get("asset_id"),
    "collection": collection.name if collection else None,
    "object_count": len(objects),
    "mesh_count": len(mesh_objs),
    "material_count": len(materials),
    "materials": materials,
    "linked_libraries": libraries,
    "missing_external_images": external_images,
    "bounds_local_m": bounds,
    "objects": [
        {"name": obj.name, "type": obj.type, "bounds": [[min((obj.matrix_world @ Vector(c))[i] for c in obj.bound_box), max((obj.matrix_world @ Vector(c))[i] for c in obj.bound_box)] for i in range(3)] if obj.type == "MESH" else None, "materials": [slot.material.name if slot.material else None for slot in obj.material_slots]}
        for obj in objects
    ],
}
out = root / "audit" / "kappa_alpha_theta" / "independent_grade_r1" / "fresh_open_probe.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: report[k] for k in report if k != "objects"}, indent=2))
