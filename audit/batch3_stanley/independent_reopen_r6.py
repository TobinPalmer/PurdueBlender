import bpy
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
asset_path = root / "modular/buildings/stanley_coulter_hall.blend"
audit = root / "audit/batch3_stanley"
expected = "ecc5c02b4eac97d2afee19602e790b86d84f41b3fe78222b17f75f43e70cc61e"
asset_hash = hashlib.sha256(asset_path.read_bytes()).hexdigest()
if asset_hash != expected:
    raise RuntimeError(f"Unexpected R6 asset hash: {asset_hash}")
collection = bpy.data.collections.get("Asset_stanley_coulter_hall")
root_obj = bpy.data.objects.get("AssetRoot_stanley_coulter_hall")
if collection is None or root_obj is None:
    raise RuntimeError("Expected asset collection/root missing")
objects = list(collection.all_objects)
meshes = [obj for obj in objects if obj.type == "MESH"]
root_data = {
    "location": list(root_obj.location),
    "rotation_euler": list(root_obj.rotation_euler),
    "scale": list(root_obj.scale),
    "world_translation": list(root_obj.matrix_world.translation),
}
depsgraph = bpy.context.evaluated_depsgraph_get()
points = []
for obj in meshes:
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        points.extend(evaluated.matrix_world @ vertex.co for vertex in mesh.vertices)
    finally:
        evaluated.to_mesh_clear()
bounds = [[min(point[i] for point in points), max(point[i] for point in points)] for i in range(3)] if points else None
materialless = []
invalid_slots = []
materials = {}
external_images = []
missing_images = []
for obj in meshes:
    slots = [slot.material for slot in obj.material_slots]
    if not slots or all(material is None for material in slots):
        materialless.append(obj.name)
    if obj.data.polygons and any(poly.material_index >= len(slots) or slots[poly.material_index] is None for poly in obj.data.polygons):
        invalid_slots.append(obj.name)
    for material in slots:
        if material:
            materials[material.name] = material
for material in materials.values():
    if not material.use_nodes:
        continue
    for node in material.node_tree.nodes:
        if node.type == "TEX_IMAGE" and node.image and node.image.source == "FILE":
            path = bpy.path.abspath(node.image.filepath)
            external_images.append({"material": material.name, "image": node.image.name, "path": path, "packed": bool(node.image.packed_file)})
            if not Path(path).exists() and not node.image.packed_file:
                missing_images.append(path)
archives = {}
for name in ("SC_Unverified_Architectural_Options_R5", "SC_Archived_Facade_Windows_R6", "SC_Archived_Entry_Fixtures_R6"):
    archive = bpy.data.collections.get(name)
    archives[name] = None if archive is None else {
        "object_count": len(archive.all_objects),
        "hidden_render": bool(archive.hide_render),
        "hidden_viewport": bool(archive.hide_viewport),
        "direct_scene_child": any(child == archive for child in bpy.context.scene.collection.children),
    }
result = {
    "asset": str(asset_path),
    "asset_sha256": asset_hash,
    "blender_version": bpy.app.version_string,
    "reopened_saved_asset": True,
    "collection": collection.name,
    "collection_object_count": len(objects),
    "mesh_count": len(meshes),
    "evaluated_bounds_local_m_xyz_axis_major": bounds,
    "root_transform": root_data,
    "material_count_used": len(materials),
    "materialless_meshes": materialless,
    "invalid_material_slot_meshes": invalid_slots,
    "file_backed_image_textures": external_images,
    "missing_external_images": missing_images,
    "recovery_archives": archives,
    "review_limit": "Standalone library check only; does not inspect or validate the master placement marker or neighborhood.",
}
(audit / "independent_reopen_r6.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2, ensure_ascii=False))
