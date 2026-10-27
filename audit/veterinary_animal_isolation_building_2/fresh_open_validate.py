import bpy, json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
asset_path = root / "modular/buildings/massing_veterinary_animal_isolation_building_2_ebb4142.blend"
out_path = Path(__file__).resolve().parent / "fresh_open_validation.json"
bpy.ops.wm.open_mainfile(filepath=str(asset_path))
scene = bpy.context.scene
collection_name = "Asset_massing_veterinary_animal_isolation_building_2_ebb4142"
collection = bpy.data.collections.get(collection_name)
assert scene.name == "Building_massing_veterinary_animal_isolation_building_2_ebb4142"
assert collection is not None
assert scene.get("building_id") == "massing_veterinary_animal_isolation_building_2_ebb4142"
objects = list(collection.objects)
verts = [obj.matrix_world @ v.co for obj in objects if obj.type == "MESH" for v in obj.data.vertices]
mins = [min(v[i] for v in verts) for i in range(3)]
maxs = [max(v[i] for v in verts) for i in range(3)]
report = {
    "asset": str(asset_path),
    "scene": scene.name,
    "asset_collection": collection.name,
    "building_id": scene.get("building_id"),
    "origin_xy_m": list(scene.get("origin_xy_m")),
    "asset_object_count": len(objects),
    "asset_object_types": {t: sum(o.type == t for o in objects) for t in sorted({o.type for o in objects})},
    "unique_material_count": len({m.name for o in objects for m in o.data.materials if m}),
    "bounds_local_m": {"min": mins, "max": maxs, "size": [maxs[i]-mins[i] for i in range(3)]},
    "image_datablocks": [img.name for img in bpy.data.images if img.source == "FILE"],
    "asset_members_are_local_objects": all(o.library is None for o in objects),
    "readback_fresh_process": True,
}
out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
