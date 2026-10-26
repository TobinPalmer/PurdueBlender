"""Independent fresh-process reopen probe for Stanley Coulter Hall R4."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular/buildings/stanley_coulter_hall.blend"
OUT = ROOT / "audit/batch3_stanley/independent_reopen_r4.json"
EXPECTED_SHA = "40c1b209881cc7eaba71b1cb0057dc6d735751dd81bf2142ba5b3e4838f03a13"
COLLECTION_NAME = "Asset_stanley_coulter_hall"
ROOT_NAME = "AssetRoot_stanley_coulter_hall"


def bbox_local(collection, include_hidden=True):
    points = []
    for obj in collection.all_objects:
        if obj.type != "MESH":
            continue
        if not include_hidden and (obj.hide_render or obj.hide_get()):
            continue
        points.extend(obj.matrix_world @ __import__("mathutils").Vector(corner) for corner in obj.bound_box)
    if not points:
        return None
    return [[min(point[i] for point in points), max(point[i] for point in points)] for i in range(3)]


asset_sha = hashlib.sha256(ASSET.read_bytes()).hexdigest()
collection = bpy.data.collections.get(COLLECTION_NAME)
root = bpy.data.objects.get(ROOT_NAME)
if collection is None or root is None:
    raise RuntimeError("Expected asset collection or root is missing after fresh open")
objects = list(collection.all_objects)
meshes = [obj for obj in objects if obj.type == "MESH"]
images = []
for image in bpy.data.images:
    if image.source in {"GENERATED", "VIEWER", "TILED"} or image.packed_file:
        continue
    path = Path(bpy.path.abspath(image.filepath)) if image.filepath else None
    if path is not None and not path.exists():
        images.append({"name": image.name, "filepath": image.filepath})
materialless = [obj.name for obj in meshes if not obj.data.materials or all(mat is None for mat in obj.data.materials)]
result = {
    "asset": "modular/buildings/stanley_coulter_hall.blend",
    "sha256": asset_sha,
    "expected_sha256": EXPECTED_SHA,
    "hash_matches_expected": asset_sha == EXPECTED_SHA,
    "fresh_reopen": bpy.data.filepath == str(ASSET),
    "blender_version": bpy.app.version_string,
    "collection": COLLECTION_NAME,
    "collection_object_count": len(objects),
    "mesh_count": len(meshes),
    "materialless_meshes": materialless,
    "missing_external_images": images,
    "root": {
        "name": root.name,
        "location": list(root.location),
        "rotation_euler": list(root.rotation_euler),
        "scale": list(root.scale),
        "matrix_world": [list(row) for row in root.matrix_world],
    },
    "bounds_local_m": bbox_local(collection),
    "render_visible_bounds_local_m": bbox_local(collection, include_hidden=False),
    "source_gis_comparison": "Official Purdue campus-map feature 56; see independent scorecard and build report; not a survey",
}
OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2, ensure_ascii=False))
if asset_sha != EXPECTED_SHA or len(objects) != 825 or materialless or images:
    raise RuntimeError("Independent fresh reopen checks did not all pass")
