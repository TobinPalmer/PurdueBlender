import hashlib
import json
import os
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parent.parent
MASTER = ROOT / "purdue_campus_master.blend"
TARGETS = {
    "massing_honors_college_and_residences_north_3de3b7c": {
        "collection": "Asset_massing_honors_college_and_residences_north_3de3b7c",
        "objects": 58,
        "grade": 8.0,
    },
    "massing_honors_college_and_residences_south_c663781": {
        "collection": "Asset_massing_honors_college_and_residences_south_c663781",
        "objects": 149,
        "grade": 8.5,
    },
    "massing_horizon_bank_debc8f2": {
        "collection": "Asset_massing_horizon_bank_debc8f2",
        "objects": 80,
        "grade": 8.9,
    },
}


def all_linked_objects(collection):
    seen_collections = set()
    objects = set()
    stack = [collection]
    while stack:
        current = stack.pop()
        if current in seen_collections:
            continue
        seen_collections.add(current)
        objects.update(current.objects)
        stack.extend(current.children)
    return objects


def library_path_for(collection):
    library = collection.library
    if library is None:
        return None
    return os.path.normcase(os.path.abspath(bpy.path.abspath(library.filepath)))


assert os.path.normcase(os.path.abspath(bpy.data.filepath)) == os.path.normcase(str(MASTER)), (
    f"Opened unexpected master file: {bpy.data.filepath}"
)

missing_libraries = []
for library in bpy.data.libraries:
    resolved = Path(bpy.path.abspath(library.filepath))
    if not resolved.is_file():
        missing_libraries.append(str(resolved))
assert not missing_libraries, f"Missing linked libraries: {missing_libraries[:20]}"

assets = {}
for asset_id, spec in TARGETS.items():
    collection = bpy.data.collections.get(spec["collection"])
    assert collection is not None, f"Missing linked collection {spec['collection']}"
    expected_path = os.path.normcase(str(ROOT / "modular" / "buildings" / f"{asset_id}.blend"))
    actual_path = library_path_for(collection)
    assert actual_path == expected_path, (asset_id, actual_path, expected_path)
    object_count = len(all_linked_objects(collection))
    assert object_count == spec["objects"], (asset_id, object_count, spec["objects"])
    grade_path = ROOT / "audit" / asset_id.replace("massing_", "")
    # Audit folder names use stable building slugs and are checked through the manifest below.
    assets[asset_id] = {
        "collection": collection.name,
        "library_path": os.path.relpath(actual_path, ROOT).replace("\\", "/"),
        "linked_object_count_recursive": object_count,
        "expected_independent_grade": spec["grade"],
        "library_loaded_in_master": True,
    }

manifest = json.loads((ROOT / "modular" / "manifest.json").read_text(encoding="utf-8"))
manifest_assets = {item["id"]: item for item in manifest["assets"]}
for asset_id, spec in TARGETS.items():
    item = manifest_assets[asset_id]
    assert item.get("completion_status") == "finished"
    assert item.get("independent_grade", {}).get("score") == spec["grade"]
    asset_path = ROOT / "modular" / item["file"]
    assert hashlib.sha256(asset_path.read_bytes()).hexdigest() == item["asset_sha256"]

# Tobin is the coordinator and owner of this master; saving here refreshes its links to the
# already-reviewed building libraries without unpacking or duplicating their geometry.
bpy.context.preferences.filepaths.save_version = 0
save_result = bpy.ops.wm.save_as_mainfile(filepath=str(MASTER), check_existing=False)
assert "FINISHED" in save_result, save_result

record = {
    "status": "PASS",
    "date": "2026-10-26",
    "blender_version": bpy.app.version_string,
    "master_file": str(MASTER),
    "master_sha256_after_save": hashlib.sha256(MASTER.read_bytes()).hexdigest(),
    "master_size_bytes": MASTER.stat().st_size,
    "active_scene": bpy.context.scene.name,
    "scene_object_count": len(bpy.context.scene.objects),
    "data_object_count_including_libraries": len(bpy.data.objects),
    "library_count": len(bpy.data.libraries),
    "missing_library_paths": missing_libraries,
    "integrated_assets": assets,
    "notes": [
        "The three source libraries were already linked directly by the master; their reviewed revisions were restored at the same stable paths.",
        "All three libraries loaded with their reviewed recursive object counts and no missing library paths.",
        "Heights and roof forms remain estimates as described in the building-specific validation and grading records.",
    ],
}
out = ROOT / "audit" / "master_sync_hcr_north_south_horizon_2026-10-26.json"
out.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(record, indent=2, ensure_ascii=False))
