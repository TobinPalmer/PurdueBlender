"""Independent fresh-open asset probe for Gemini Cooperative House."""
import hashlib
import json
from pathlib import Path

import bpy

ROOT = Path(bpy.data.filepath).resolve().parents[2]
ASSET = Path(bpy.data.filepath).resolve()
scene = bpy.context.scene
collection_name = "Asset_massing_gemini_cooperative_fid825"
collection = bpy.data.collections.get(collection_name)
objects = list(collection.all_objects) if collection else []
meshes = [obj for obj in objects if obj.type == "MESH"]
materials = sorted({slot.material.name for obj in meshes for slot in obj.material_slots if slot.material})
missing_materials = sorted(obj.name for obj in meshes if not any(slot.material for slot in obj.material_slots))
linked_libraries = sorted(str(Path(bpy.path.abspath(lib.filepath)).resolve()) for lib in bpy.data.libraries)
external_images = sorted(img.filepath for img in bpy.data.images if img.source == "FILE" and not img.packed_file)
names = sorted(obj.name for obj in objects)

result = {
    "asset": str(ASSET),
    "sha256": hashlib.sha256(ASSET.read_bytes()).hexdigest(),
    "blender_version": bpy.app.version_string,
    "scene": scene.name,
    "collection": collection.name if collection else None,
    "object_count": len(objects),
    "mesh_count": len(meshes),
    "vertex_count": sum(len(obj.data.vertices) for obj in meshes),
    "polygon_count": sum(len(obj.data.polygons) for obj in meshes),
    "materials": materials,
    "mesh_objects_without_material": missing_materials,
    "linked_libraries": linked_libraries,
    "unpacked_external_images": external_images,
    "object_names": names,
    "interior_name_matches": [n for n in names if any(t in n.lower() for t in ("room", "bed", "kitchen", "table", "chair", "sofa", "corridor", "interior", "bath", "lounge"))],
}
out = ROOT / "audit" / "gemini" / "independent_grade_r1" / "fresh_open_probe.json"
out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({k: v for k, v in result.items() if k != "object_names"}, indent=2, ensure_ascii=False))
