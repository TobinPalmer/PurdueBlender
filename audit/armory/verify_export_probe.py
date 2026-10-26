from pathlib import Path
import json
import bpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROBE = HERE / "armory_asset_collection_probe.blend"
bpy.ops.wm.open_mainfile(filepath=str(PROBE))
asset = bpy.data.collections.get("Asset_armory")
assert asset is not None
assert asset.get("building_id") == "armory"
assert asset.get("owner") == "Rosen"
assert asset.get("source_feature_id") == 207
assert bpy.data.objects.get("Armory_Rosen_Central_Stepped_Gable")
assert not any(o.type in {"CAMERA", "LIGHT"} for o in asset.all_objects)
print(json.dumps({"reopened_export_probe": str(PROBE),
                  "collection": asset.name,
                  "object_count": len(asset.all_objects),
                  "central_gable": True,
                  "camera_or_light_in_export": False}, indent=2))
