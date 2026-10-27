"""Fresh-process structural validation for the Theta Chi modular blend."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular" / "buildings" / "massing_house_301841328_39f169f.blend"
OUT = ROOT / "audit" / "theta_chi" / "reopen_validation.json"
COLLECTION_NAME = "Asset_massing_house_301841328_39f169f"
OBJECT_NAME = "House_301841328"

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
bpy.context.view_layer.update()
collection = bpy.data.collections.get(COLLECTION_NAME)
assert collection is not None, f"Missing collection {COLLECTION_NAME}"
objects = list(collection.objects)
assert len(objects) == 1, f"Expected exactly one library asset object, found {len(objects)}"
obj = objects[0]
assert obj.name == OBJECT_NAME and obj.type == "MESH"
assert not obj.modifiers, f"Unexpected unevaluated modifiers: {[m.name for m in obj.modifiers]}"
assert all(abs(v) < 1e-8 for v in obj.location), f"Unexpected object translation: {tuple(obj.location)}"
assert all(abs(v) < 1e-8 for v in obj.rotation_euler), f"Unexpected object rotation: {tuple(obj.rotation_euler)}"
assert all(abs(v-1.0) < 1e-8 for v in obj.scale), f"Unexpected object scale: {tuple(obj.scale)}"

world = [obj.matrix_world @ __import__("mathutils").Vector(c) for c in obj.bound_box]
bounds = [[min(v[i] for v in world), max(v[i] for v in world)] for i in range(3)]
external_images = [im.filepath for im in bpy.data.images if im.source == "FILE" and im.filepath]
external_libraries = [lib.filepath for lib in bpy.data.libraries if lib.filepath]
report = {
    "asset": str(ASSET.relative_to(ROOT)).replace("\\", "/"),
    "blender_version": bpy.app.version_string,
    "reopened_in_fresh_process": True,
    "collection": COLLECTION_NAME,
    "collection_object_count": len(objects),
    "object": OBJECT_NAME,
    "object_type": obj.type,
    "mesh_vertex_count": len(obj.data.vertices),
    "mesh_edge_count": len(obj.data.edges),
    "mesh_face_count": len(obj.data.polygons),
    "material_slots": [slot.material.name if slot.material else None for slot in obj.material_slots],
    "bounds_world_m": bounds,
    "object_transform_identity": True,
    "modifiers": [],
    "external_images": external_images,
    "external_libraries": external_libraries,
    "portable": not external_images and not external_libraries,
    "blend_sha256": hashlib.sha256(ASSET.read_bytes()).hexdigest(),
}
OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
assert report["portable"], f"External dependencies found: {external_images + external_libraries}"
print("THETA_CHI_REOPEN_VALIDATION=" + json.dumps(report, sort_keys=True))
