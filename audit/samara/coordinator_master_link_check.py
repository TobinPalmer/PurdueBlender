"""Read the campus master to verify SAMARA's existing link; never save it."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
MASTER = ROOT / "purdue_campus_master.blend"
ASSET = ROOT / "modular/buildings/massing_samara_f6b8e61.blend"
NAME = "Asset_massing_samara_f6b8e61"


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


before = digest(MASTER)
asset_digest = digest(ASSET)
bpy.ops.wm.open_mainfile(filepath=str(MASTER), load_ui=False)
target = bpy.data.collections.get(NAME)


def occurrences(collection):
    return sum((1 if child == target else 0) + occurrences(child)
               for child in collection.children)


direct = occurrences(bpy.context.scene.collection) if target else 0
instances = [o.name for o in bpy.context.scene.objects
             if o.instance_type == "COLLECTION" and o.instance_collection == target]
points = []
if target:
    for obj in target.all_objects:
        if obj.type == "MESH":
            points.extend(obj.matrix_world @ Vector(v) for v in obj.bound_box)
library_path = (Path(bpy.path.abspath(target.library.filepath)).resolve()
                if target and target.library else None)
after = digest(MASTER)
result = {
    "checked_utc": datetime.now(timezone.utc).isoformat(),
    "master": str(MASTER.relative_to(ROOT)),
    "asset": str(ASSET.relative_to(ROOT)),
    "asset_sha256": asset_digest,
    "expected_collection": NAME,
    "collection_found": target is not None,
    "linked_from_expected_asset": library_path == ASSET.resolve(),
    "direct_collection_occurrences": direct,
    "collection_instances": instances,
    "mesh_count": len([o for o in target.all_objects if o.type == "MESH"]) if target else 0,
    "world_bounds_m": [[min(p[i] for p in points), max(p[i] for p in points)]
                       for i in range(3)] if points else None,
    "master_sha256_before": before,
    "master_sha256_after": after,
    "master_unchanged": before == after,
    "saved_master": False,
}
result["passed"] = (result["linked_from_expected_asset"] and
                    direct + len(instances) == 1 and result["master_unchanged"])
(Path(__file__).parent / "master_link_check.json").write_text(
    json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
