import json
from pathlib import Path
import bpy
from mathutils import Vector

BUILDING_ID = "massing_house_301841252_e4f8f05"
EXPECTED_COLLECTION = f"Asset_{BUILDING_ID}"
EXPECTED_SCENE = f"Building_{BUILDING_ID}"
ASSET = Path(__file__).resolve().parents[2] / "modular" / "buildings" / f"{BUILDING_ID}.blend"
OUT = Path(__file__).resolve().parent / "reopen_validation.json"

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene = bpy.context.scene
collection = bpy.data.collections.get(EXPECTED_COLLECTION)
assert scene.name == EXPECTED_SCENE, (scene.name, EXPECTED_SCENE)
assert collection is not None
assert "House_301841252" in collection.objects
assert len(collection.objects) > 500
assert scene.get("building_id") == BUILDING_ID
assert scene.get("gis_source", "").endswith("FID 790")

depsgraph = bpy.context.evaluated_depsgraph_get()
coords = []
mesh_objects = 0
modified_objects = 0
missing_material_objects = []
external_images = []
for obj in collection.objects:
    if obj.type not in {"MESH", "FONT", "CURVE", "SURFACE", "META"}:
        continue
    ev = obj.evaluated_get(depsgraph)
    try:
        mesh = ev.to_mesh()
        if mesh is None:
            continue
        mesh_objects += 1
        if obj.modifiers:
            modified_objects += 1
        if not obj.data.materials:
            missing_material_objects.append(obj.name)
        coords.extend(tuple(ev.matrix_world @ v.co) for v in mesh.vertices)
    finally:
        if ev.type != "FONT":
            ev.to_mesh_clear()
for img in bpy.data.images:
    if img.source == "FILE" and img.filepath and not img.packed_file:
        external_images.append(img.filepath)
mins = [min(v[i] for v in coords) for i in range(3)]
maxs = [max(v[i] for v in coords) for i in range(3)]
result = {
    "building_id": BUILDING_ID,
    "asset": "modular/buildings/massing_house_301841252_e4f8f05.blend",
    "fresh_reopen": True,
    "scene_name": scene.name,
    "expected_scene_name": EXPECTED_SCENE,
    "collection": EXPECTED_COLLECTION,
    "collection_object_count": len(collection.objects),
    "evaluated_mesh_object_count": mesh_objects,
    "evaluated_bounds_world_m": [mins, maxs],
    "dimensions_world_m": [maxs[i]-mins[i] for i in range(3)],
    "modifier_object_count": modified_objects,
    "missing_material_objects": missing_material_objects,
    "unpacked_external_image_paths": external_images,
    "source_identity": scene.get("gis_source"),
    "vertical_uncertainty": scene.get("vertical_uncertainty"),
    "checks": {
        "expected_collection_present": True,
        "expected_scene_present": True,
        "expected_root_asset_object_present": True,
        "more_than_500_asset_objects": True,
        "all_evaluated_geometry_nonempty": bool(coords),
        "all_assets_have_materials": not missing_material_objects,
        "no_unpacked_external_images": not external_images
    }
}
OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
