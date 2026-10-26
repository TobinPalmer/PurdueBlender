"""Check that model geometry intended for export is in the named asset collection."""
import hashlib
import json
from pathlib import Path

import bpy

root = Path(__file__).resolve().parent
asset = bpy.data.collections.get("Asset_tarkington_hall")
if asset is None:
    raise RuntimeError("Missing Asset_tarkington_hall")
scene = bpy.context.scene
all_names = {obj.name for obj in asset.all_objects}
connector_records = []
outside = []
for obj in bpy.data.objects:
    if "Connector" in obj.name:
        record = {
            "name": obj.name,
            "type": obj.type,
            "collections": [col.name for col in obj.users_collection],
            "in_export_collection": obj.name in all_names,
        }
        connector_records.append(record)
        if obj.name not in all_names:
            outside.append(obj.name)
report = {
    "asset_sha256": hashlib.sha256(Path(bpy.data.filepath).resolve().read_bytes()).hexdigest(),
    "asset_scene": scene.name,
    "scene_object_count": len(scene.objects),
    "database_object_count": len(bpy.data.objects),
    "export_collection_object_count": len(asset.all_objects),
    "export_collection_mesh_count": sum(1 for obj in asset.all_objects if obj.type == "MESH"),
    "export_object_names": sorted(obj.name for obj in asset.all_objects),
    "scene_child_collections": [col.name for col in scene.collection.children],
    "connector_count_database": len(connector_records),
    "connector_count_in_export": sum(1 for rec in connector_records if rec["in_export_collection"]),
    "connector_objects_outside_export": outside,
    "connector_records": connector_records,
}
(root / "independent_membership_r2.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
