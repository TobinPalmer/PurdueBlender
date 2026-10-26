"""Append the Alpha Chi Rho collection to a clean scene, save, and reopen it."""

import json
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_alpha_chi_rho_0cb591a"
COLLECTION = "Asset_massing_alpha_chi_rho_0cb591a"
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
PROBE = ROOT / "audit" / "alpha_chi_rho" / "clean_scene_import_probe.blend"
OUTPUT = ROOT / "audit" / "alpha_chi_rho" / "export_reopen_probe.json"

with bpy.data.libraries.load(str(ASSET), link=False) as (data_from, data_to):
    assert COLLECTION in data_from.collections, data_from.collections[:]
    data_to.collections = [COLLECTION]

imported = data_to.collections[0]
assert imported is not None
bpy.context.scene.collection.children.link(imported)
assert imported.name == COLLECTION
assert len(imported.objects) == 1
bpy.ops.wm.save_as_mainfile(filepath=str(PROBE))

# Reopen the generated deliverable itself, then check its portable collection.
bpy.ops.wm.open_mainfile(filepath=str(PROBE))
scene = bpy.context.scene
collection = bpy.data.collections.get(COLLECTION)
assert collection is not None
objects = list(collection.objects)
assert len(objects) == 1
obj = objects[0]
assert obj.name == "Alpha Chi Rho" and obj.type == "MESH"
assert len(obj.data.materials) == 7
assert all(material is not None for material in obj.data.materials)
external_images = [image.filepath for image in bpy.data.images
                   if image.source == "FILE" and image.filepath]
assert not external_images, external_images
result = {
    "status": "PASS",
    "source_asset": str(ASSET),
    "probe_file": str(PROBE),
    "reopened_probe_file": bpy.data.filepath,
    "scene": scene.name,
    "collection": collection.name,
    "collection_object_count": len(objects),
    "object_name": obj.name,
    "object_type": obj.type,
    "mesh_vertices": len(obj.data.vertices),
    "mesh_polygons": len(obj.data.polygons),
    "material_count": len(obj.data.materials),
    "external_image_dependencies": external_images,
}
OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
