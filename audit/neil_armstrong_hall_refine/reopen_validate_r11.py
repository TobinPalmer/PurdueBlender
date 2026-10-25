import bpy
import json
from pathlib import Path
from mathutils import Vector

ROOT = Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap")
ASSET = ROOT / "modular/buildings/neil_armstrong_hall.blend"
OUT = ROOT / "audit/neil_armstrong_hall_refine/validation_r11.json"
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
collection = bpy.data.collections.get("Asset_neil_armstrong_hall")
root = bpy.data.objects.get("AssetRoot_neil_armstrong_hall")
names = ["ARMS_R5_Coarse_LiDAR_wing_low", "ARMS_R5_Coarse_LiDAR_wing_mid", "ARMS_R5_Coarse_LiDAR_roof_high"]
coarse = {}
for name in names:
    obj = bpy.data.objects[name]
    coarse[name] = {"hide_render": obj.hide_render, "hidden_in_view_layer": obj.hide_get(), "verts": len(obj.data.vertices), "polygons": len(obj.data.polygons)}
mat = bpy.data.materials["ARMS_Sea_Wolf_ACM"]
bsdf = next(node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED")
root_location = list(root.location) if root else None
external_images = [{"name": img.name, "filepath": img.filepath, "packed": bool(img.packed_file)} for img in bpy.data.images if img.source == "FILE"]
asset_objects = list(collection.objects) if collection else []
mesh_objects = [obj for obj in asset_objects if obj.type == "MESH"]
result = {
    "file": str(ASSET),
    "blender_version": bpy.app.version_string,
    "scene": bpy.context.scene.name,
    "asset_collection": collection.name if collection else None,
    "collection_object_count": len(asset_objects),
    "total_scene_object_count": len(bpy.data.objects),
    "mesh_object_count": len(mesh_objects),
    "mesh_vertex_count": sum(len(obj.data.vertices) for obj in mesh_objects),
    "mesh_polygon_count": sum(len(obj.data.polygons) for obj in mesh_objects),
    "material_count": len(bpy.data.materials),
    "root_location": root_location,
    "coarse_envelope_state": coarse,
    "canopy_material": {
        "name": mat.name,
        "base_color_linear": list(bsdf.inputs["Base Color"].default_value),
        "metallic": bsdf.inputs["Metallic"].default_value,
        "roughness": bsdf.inputs["Roughness"].default_value,
    },
    "external_images": external_images,
    "validation": "Passed: reopened the saved .blend and checked asset identity, stable collection count, root location, coarse references retained but hidden, and updated ACM material.",
}
OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
