import hashlib
import json
import os
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parent.parent
MASTER = ROOT / "purdue_campus_master.blend"
TARGETS = {
    "massing_honors_college_and_residences_north_3de3b7c": (58, 8.0),
    "massing_honors_college_and_residences_south_c663781": (149, 8.5),
    "massing_horizon_bank_debc8f2": (80, 8.9),
}


def recursively_count(collection):
    seen_collections = set()
    seen_objects = set()
    stack = [collection]
    while stack:
        current = stack.pop()
        if current in seen_collections:
            continue
        seen_collections.add(current)
        seen_objects.update(current.objects)
        stack.extend(current.children)
    return len(seen_objects)


assert os.path.normcase(os.path.abspath(bpy.data.filepath)) == os.path.normcase(str(MASTER))
missing = [
    str(Path(bpy.path.abspath(lib.filepath)))
    for lib in bpy.data.libraries
    if not Path(bpy.path.abspath(lib.filepath)).is_file()
]
assert not missing, missing[:20]

manifest = json.loads((ROOT / "modular" / "manifest.json").read_text(encoding="utf-8"))
records = {item["id"]: item for item in manifest["assets"]}
assets = {}
for asset_id, (expected_count, expected_score) in TARGETS.items():
    record = records[asset_id]
    collection = bpy.data.collections.get(record["collection"])
    assert collection is not None, asset_id
    assert recursively_count(collection) == expected_count, asset_id
    source_path = ROOT / "modular" / record["file"]
    source_sha = hashlib.sha256(source_path.read_bytes()).hexdigest()
    assert source_sha == record["asset_sha256"]
    assert record["independent_grade"]["score"] == expected_score
    assert record["independent_grade"]["passed"] is True
    assert os.path.normcase(os.path.abspath(bpy.path.abspath(collection.library.filepath))) == os.path.normcase(str(source_path))
    assets[asset_id] = {
        "library_path": record["file"],
        "asset_sha256": source_sha,
        "recursive_object_count": expected_count,
        "independent_grade": expected_score,
        "linked_on_reopen": True,
    }

result = {
    "status": "PASS",
    "fresh_open_after_master_save": True,
    "date": "2026-10-26",
    "blender_version": bpy.app.version_string,
    "master_file": str(MASTER),
    "master_sha256": hashlib.sha256(MASTER.read_bytes()).hexdigest(),
    "scene": bpy.context.scene.name,
    "scene_object_count": len(bpy.context.scene.objects),
    "data_object_count_including_libraries": len(bpy.data.objects),
    "library_count": len(bpy.data.libraries),
    "missing_libraries": missing,
    "assets": assets,
}
output = ROOT / "audit" / "master_fresh_open_hcr_north_south_horizon_2026-10-26.json"
output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2, ensure_ascii=False))
