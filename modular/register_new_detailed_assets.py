"""Register recently built detailed building libraries in the modular manifest."""
import bpy
import json
from pathlib import Path
from mathutils import Vector

MODULAR = Path(__file__).resolve().parent
BUILDINGS = MODULAR / "buildings"
MANIFEST_PATH = MODULAR / "manifest.json"
manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

NEW_ASSETS = [
    "benjamin_harrison_hall",
    "hansen_life_sciences",
    "hicks_library",
    "krannert_building",
    "lawson_hall",
    "mccutcheon_hall",
    "niswonger_aviation_tech",
    "rawls_hall",
    "stanley_coulter_hall",
]

by_id = {a["id"]: a for a in manifest["assets"]}
added = []
for asset_id in NEW_ASSETS:
    if asset_id in by_id:
        continue
    path = BUILDINGS / f"{asset_id}.blend"
    collection_name = f"Asset_{asset_id}"
    scene_name = f"Building_{asset_id}"
    with bpy.data.libraries.load(str(path), link=False) as (src, dst):
        if collection_name not in src.collections:
            raise RuntimeError(f"{collection_name} not found in {path.name}")
        if scene_name not in src.scenes:
            raise RuntimeError(f"{scene_name} not found in {path.name}")
        dst.collections = [collection_name]
        dst.scenes = [scene_name]
    collection = bpy.data.collections.get(collection_name)
    scene = bpy.data.scenes.get(scene_name)
    objects = list(collection.all_objects)
    geometry = [o for o in objects if o.type in {"MESH", "CURVE", "FONT", "SURFACE", "META"}]
    points = [o.matrix_world @ Vector(corner) for o in geometry for corner in o.bound_box]
    bounds = [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)] if points else None
    record = {
        "id": asset_id,
        "kind": "detailed",
        "file": f"buildings/{asset_id}.blend",
        "collection": collection_name,
        "scene": scene_name,
        "objects": [o.name for o in objects],
        "object_count": len(objects),
        "bounds_world_m": bounds,
        "exterior_bounds_world_m": bounds,
        "accuracy_status": "unverified; see ../audit/MASTER_AUDIT.md",
        "placement_transform": "world coordinates retained in asset; pending local-origin master placement",
        "source_metadata": {k: scene.get(k) for k in scene.keys()},
    }
    manifest["assets"].append(record)
    by_id[asset_id] = record
    added.append(asset_id)

MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(json.dumps({"registered": added, "asset_count": len(manifest["assets"])}))
