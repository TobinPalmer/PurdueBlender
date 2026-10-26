import bpy
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
asset = root / "modular/buildings/walc.blend"
report_path = root / "audit/walc_refine/independent_grade_r3_reopen.json"
collection = bpy.data.collections.get("Asset_walc")
scene = bpy.data.scenes.get("Building_walc")
root_obj = bpy.data.objects.get("AssetRoot_walc")
if collection is None or scene is None or root_obj is None:
    raise RuntimeError("Expected WALC scene, export collection, or root object is missing")
objects = list(collection.all_objects)
meshes = [obj for obj in objects if obj.type == "MESH"]
materials = {}
materialless = []
invalid_slots = []
for obj in meshes:
    slots = [slot.material for slot in obj.material_slots]
    if not slots or all(material is None for material in slots):
        materialless.append(obj.name)
    if obj.data.polygons and any(poly.material_index >= len(slots) or slots[poly.material_index] is None for poly in obj.data.polygons):
        invalid_slots.append(obj.name)
    for material in slots:
        if material is not None:
            materials[material.name] = material
image_nodes = []
missing_images = []
for material in materials.values():
    if not material.use_nodes:
        continue
    for node in material.node_tree.nodes:
        if node.type == "TEX_IMAGE" and node.image:
            image = node.image
            path = bpy.path.abspath(image.filepath) if image.source == "FILE" else None
            packed = bool(image.packed_file)
            image_nodes.append({"material": material.name, "image": image.name, "packed": packed, "path": path})
            if image.source == "FILE" and path and not Path(path).exists() and not packed:
                missing_images.append(path)
libraries = []
missing_libraries = []
for library in bpy.data.libraries:
    resolved = Path(bpy.path.abspath(library.filepath)).resolve()
    exists = resolved.exists()
    libraries.append({"name": library.name, "filepath": library.filepath, "resolved_path": str(resolved), "exists": exists})
    if not exists:
        missing_libraries.append(str(resolved))
depsgraph = bpy.context.evaluated_depsgraph_get()
points = []
for obj in meshes:
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        points.extend(evaluated.matrix_world @ vertex.co for vertex in mesh.vertices)
    finally:
        evaluated.to_mesh_clear()
bounds = [[min(point[axis] for point in points), max(point[axis] for point in points)] for axis in range(3)] if points else None
result = {
    "asset": str(asset),
    "sha256": hashlib.sha256(asset.read_bytes()).hexdigest(),
    "expected_sha256": "c9ca2cfe413898780445bade8e729e22510535aed123407c4d11e5c28f53ec65",
    "hash_matches_expected": hashlib.sha256(asset.read_bytes()).hexdigest() == "c9ca2cfe413898780445bade8e729e22510535aed123407c4d11e5c28f53ec65",
    "blender_version": bpy.app.version_string,
    "fresh_reopen": True,
    "scene": scene.name,
    "collection": collection.name,
    "collection_object_count": len(objects),
    "mesh_count": len(meshes),
    "material_count_used": len(materials),
    "materialless_meshes": materialless,
    "invalid_material_slot_meshes": invalid_slots,
    "image_texture_nodes": image_nodes,
    "missing_external_images": missing_images,
    "linked_libraries": libraries,
    "missing_libraries": missing_libraries,
    "root_transform": {"name": root_obj.name, "location": list(root_obj.location), "rotation_euler": list(root_obj.rotation_euler), "scale": list(root_obj.scale), "matrix_world": [[float(root_obj.matrix_world[r][c]) for c in range(4)] for r in range(4)]},
    "evaluated_bounds_local_m": bounds,
    "limits": ["Standalone library reopen only; no master Placement_walc marker or neighbor check. The cached GIS trace agreement repeats the source used to author the geometry and is not independent survey evidence."]
}
report_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2, ensure_ascii=False))
