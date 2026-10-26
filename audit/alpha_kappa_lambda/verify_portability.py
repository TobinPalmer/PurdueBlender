from pathlib import Path
import json
import bpy
ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_alpha_kappa_lambda_88dda6c"
ASSET_PATH = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
COLLECTION = f"Asset_{ASSET_ID}"
SCENE = f"Building_{ASSET_ID}"
RESULT = ROOT / "audit" / "alpha_kappa_lambda" / "portability_check.json"
bpy.ops.wm.open_mainfile(filepath=str(ASSET_PATH))
assert bpy.context.scene.name == SCENE
source = bpy.data.collections.get(COLLECTION)
assert source is not None and len(source.objects) == 1
obj = source.objects[0]
assert obj.name == "Alpha Kappa Lambda" and obj.type == "MESH"
assert tuple(round(v, 5) for v in obj.location) == (0.0, 0.0, 0.0)
assert not obj.modifiers
bounds = [[min(v[i] for v in obj.bound_box), max(v[i] for v in obj.bound_box)] for i in range(3)]
object_name, object_type, count = obj.name, obj.type, len(source.objects)
external = [i.filepath for i in bpy.data.images if i.source == "FILE" and i.filepath and not i.packed_file]
assert not external, external
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(ASSET_PATH), link=True) as (src, dst):
    assert COLLECTION in src.collections
    dst.collections = [COLLECTION]
linked = bpy.data.collections.get(COLLECTION)
assert linked is not None
bpy.context.scene.collection.children.link(linked)
assert len(linked.objects) == 1
linked_obj = linked.objects[0]
assert linked_obj.name == "Alpha Kappa Lambda" and linked_obj.type == "MESH"
assert tuple(round(v, 5) for v in linked_obj.location) == (0.0, 0.0, 0.0)
report = {"asset_id": ASSET_ID, "asset_path": str(ASSET_PATH.relative_to(ROOT)).replace("\\", "/"), "reopened_scene": SCENE, "reopened_collection": COLLECTION, "object_count": count, "object_name": object_name, "object_type": object_type, "object_transform": "identity", "modifiers": 0, "world_bounds_m": bounds, "linked_into_fresh_empty_file": True, "linked_collection_objects": len(linked.objects), "unpacked_external_image_dependencies": external, "result": "PASS"}
RESULT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
