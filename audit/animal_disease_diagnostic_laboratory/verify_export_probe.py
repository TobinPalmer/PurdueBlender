from pathlib import Path
import json
import bpy

HERE = Path(__file__).resolve().parent
PROBE = HERE / "collection_export_probe.blend"
EXPECTED = "Asset_animal_disease_diagnostic_laboratory"
bpy.ops.wm.open_mainfile(filepath=str(PROBE))
collection = bpy.data.collections.get(EXPECTED)
assert collection is not None
assert collection.get("building_id") == "animal_disease_diagnostic_laboratory"
assert collection.get("source_feature_id") == 241
assert len(collection.objects) == 8
assert all(obj.type not in {"CAMERA", "LIGHT"} for obj in collection.objects)
print(json.dumps({"reopened_collection_export": str(PROBE),
                  "collection": EXPECTED,
                  "object_count": len(collection.objects),
                  "object_names": sorted(obj.name for obj in collection.objects)}, indent=2))
