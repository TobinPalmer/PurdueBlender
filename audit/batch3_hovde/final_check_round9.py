import bpy, json
from pathlib import Path

PROJECT = Path(r"C:/Users/Tobin/Documents/Blender/PurdueMap")
ASSET = PROJECT / "modular/buildings/hovde_hall.blend"
OUT = PROJECT / "audit/batch3_hovde/final_asset_check_round9.json"
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
collection = bpy.data.collections["Asset_hovde_hall"]
root = bpy.data.objects["HOVD_Root"]
objects = list(collection.all_objects)
meshes = [obj for obj in objects if obj.type == "MESH"]
unmaterialed = [obj.name for obj in meshes if not obj.data.materials]
columns = {}
for i in range(1, 7):
    obj = bpy.data.objects[f"HOVD_Classical_Column_{i}"]
    columns[obj.name] = list(round(v, 4) for v in obj.location)
portico = {}
for name in (
    "HOVD_Portico_Entablature", "HOVD_Portico_Cornice",
    "HOVD_Portico_Pediment_Base", "HOVD_Portico_Pediment_Crown",
):
    obj = bpy.data.objects[name]
    portico[name] = {
        "location_local_m": [round(v, 4) for v in obj.location],
        "dimensions_world_aligned_m": [round(v, 4) for v in obj.dimensions],
    }
record = {
    "building": "Hovde Hall",
    "round": 9,
    "file": str(ASSET),
    "scene": "Building_hovde_hall",
    "export_collection": "Asset_hovde_hall",
    "export_objects": len(objects),
    "mesh_objects": len(meshes),
    "unmaterialed_meshes": unmaterialed,
    "material_slots_used": sorted({m.name for obj in objects for m in getattr(obj.data, "materials", []) if m}),
    "six_columns_reopened": columns,
    "portico_members": portico,
    "root_transform": {
        "location": [round(v, 6) for v in root.location],
        "rotation_euler_radians": [round(v, 6) for v in root.rotation_euler],
        "scale": [round(v, 6) for v in root.scale],
    },
    "source_photo_portico_width_ratio_estimate": 0.25,
    "source_photo_ratio_uncertainty": 0.04,
    "source_photo_ratio_note": "Measured from the nearly frontal 2016 image by comparing the pediment width with the visible long facade. This is a visual ratio estimate, not a survey dimension.",
    "master_gis_alignment_verified": False,
    "saved_asset_reopened": True,
}
OUT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
print(json.dumps(record, indent=2))
