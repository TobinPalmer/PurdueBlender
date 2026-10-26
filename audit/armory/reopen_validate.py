"""Reopen, measure the structural GIS footprint and export Asset_armory."""
from pathlib import Path
import json
import os
import bpy

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
ASSET = ROOT / "modular/buildings/armory.blend"
PROBE = HERE / "armory_asset_collection_probe.blend"
EXPECTED = "Asset_armory"

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
assert bpy.context.scene.name == "Building_armory"
asset = bpy.data.collections.get(EXPECTED)
assert asset is not None
assert asset.get("building_id") == "armory"
assert asset.get("owner") == "Rosen"
assert asset.get("source_feature_id") == 207
assert asset.get("gis_affine_fit_applied")
assert bpy.data.objects.get("Armory_Rosen_Central_Stepped_Gable")
assert all(o.type not in {"CAMERA", "LIGHT"} for o in asset.all_objects)

def bounds_for(objects):
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for obj in objects:
        if obj.type != "MESH":
            continue
        ev = obj.evaluated_get(dg)
        mesh = ev.to_mesh()
        pts.extend(ev.matrix_world @ v.co for v in mesh.vertices)
        ev.to_mesh_clear()
    return [[min(v[i] for v in pts), max(v[i] for v in pts)] for i in (0, 1, 2)]

wall_names = {"Armory_Wall_East", "Armory_Wall_West", "Armory_Wall_North_Low", "Armory_Wall_South_Low"}
walls = [o for o in asset.all_objects if o.name in wall_names]
assert len(walls) == 4
wall_bounds = bounds_for(walls)
target_bounds = [[-35.235137124349905, 15.6407920121014],
                 [-43.96725926936233, 44.644985237158835]]
for axis in (0, 1):
    assert abs(wall_bounds[axis][0] - target_bounds[axis][0]) < 0.01
    assert abs(wall_bounds[axis][1] - target_bounds[axis][1]) < 0.01

remaining_towers = [o.name for o in asset.all_objects if o.name.startswith("Armory_Tower_")]
remaining_trusses = [o.name for o in asset.all_objects if o.name.startswith("Armory_Truss_")]
assert not remaining_towers and not remaining_trusses
assert asset.get("removed_unsupported_tower_detail_count") >= 1
assert asset.get("removed_unverified_truss_detail_count") >= 1
external_image_paths = []
for image in bpy.data.images:
    if image.filepath and image.source == "FILE" and not image.packed_file:
        external_image_paths.append(image.filepath)
library_paths = [lib.filepath for lib in bpy.data.libraries]
absolute_library_paths = [p for p in library_paths if p and not p.startswith("//")]
assert not external_image_paths
assert not absolute_library_paths

object_count = len(asset.all_objects)
old_library_paths = []
for lib in bpy.data.libraries:
    old_library_paths.append((lib, lib.filepath))
    absolute = bpy.path.abspath(lib.filepath)
    relative = os.path.relpath(absolute, start=str(PROBE.parent)).replace("\\", "/")
    lib.filepath = "//" + relative
bpy.data.libraries.write(str(PROBE), {asset}, path_remap="RELATIVE_ALL", fake_user=True, compress=True)
for lib, old_path in old_library_paths:
    lib.filepath = old_path
print(json.dumps({
    "reopened_asset": str(ASSET),
    "scene": bpy.context.scene.name,
    "collection": EXPECTED,
    "collection_object_count": object_count,
    "structural_wall_bounds_local_m": wall_bounds,
    "gis_target_bounds_local_m": target_bounds,
    "removed_unsupported_tower_count": asset.get("removed_unsupported_tower_detail_count"),
    "removed_unverified_truss_count": asset.get("removed_unverified_truss_detail_count"),
    "external_unpacked_images": external_image_paths,
    "relative_libraries": library_paths,
    "absolute_library_paths": absolute_library_paths,
    "export_probe": str(PROBE),
}, indent=2))
