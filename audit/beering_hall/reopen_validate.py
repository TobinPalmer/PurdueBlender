"""Reopen Beering Hall, measure evaluated local bounds, and test collection export."""
import bpy
import json
import hashlib
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular" / "buildings" / "beering_hall.blend"
OUT = ROOT / "audit" / "beering_hall"
PROBE = OUT / "beering_hall_collection_probe.blend"
REPORT = OUT / "reopen_validation.json"
SCENE_NAME = "Building_beering_hall"
COLLECTION_NAME = "Asset_beering_hall"
EXPECTED_ORIGIN = [-201.3499984741211, -206.14999389648438]


def eval_points(obj, deps):
    ev = obj.evaluated_get(deps)
    mesh = ev.to_mesh()
    try:
        return [ev.matrix_world @ v.co for v in mesh.vertices]
    finally:
        ev.to_mesh_clear()


def bounds(points):
    return [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]


bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene = bpy.data.scenes.get(SCENE_NAME)
asset = bpy.data.collections.get(COLLECTION_NAME)
assert scene and asset
root = bpy.data.objects.get("AssetRoot_beering_hall")
assert root and root.get("building_id") == "beering_hall" and root.get("owner") == "Rosen"
assert list(root.get("placement_origin_xy_m")) == EXPECTED_ORIGIN
assert not [o.name for o in asset.all_objects if o.type in {"CAMERA", "LIGHT"}]
assert not [o.name for o in asset.all_objects if o.name.startswith(("BRNG_Rotunda_", "BRNG_Vision21_"))]
roof = [o for o in asset.all_objects if o.name.startswith("BRNG_Rooftop_Room_")]
assert len(roof) == 75, f"Unexpected rooftop room object count: {len(roof)}"
roof_names = sorted(o.name for o in roof)
assert bpy.data.objects.get("BRNG_Rooftop_Room_Flat_Crown")

deps = bpy.context.evaluated_depsgraph_get()
mesh_points = []
for obj in asset.all_objects:
    if obj.type == "MESH":
        mesh_points.extend(eval_points(obj, deps))
all_bounds = bounds(mesh_points)
structural = {}
for name in ("BRNG_Classroom_Wing_Masonry", "BRNG_Office_Tower_Masonry"):
    obj = bpy.data.objects[name]
    structural[name] = bounds(eval_points(obj, deps))
    assert obj.name in asset.objects

external_images = []
for obj in asset.all_objects:
    for slot in obj.material_slots:
        mat = slot.material
        if mat and mat.use_nodes:
            for node in mat.node_tree.nodes:
                if node.type == "TEX_IMAGE" and node.image and node.image.filepath:
                    external_images.append({"object": obj.name, "image": node.image.name,
                                            "filepath": node.image.filepath,
                                            "packed": bool(node.image.packed_file)})
assert not external_images, external_images
linked_libraries = [{"filepath": lib.filepath, "absolute": bpy.path.abspath(lib.filepath)}
                    for lib in bpy.data.libraries if lib.filepath]
assert all(not Path(item["absolute"]).is_absolute() or str(item["absolute"]).startswith(str(ROOT))
           for item in linked_libraries)

# Verify the manifest's local geometry has not been globally translated, and
# preserve the known approximate fit quality without claiming a full vertex fit.
gis = json.loads((OUT / "purdue_gis_feature_251.json").read_text(encoding="utf-8"))
ring = gis["features"][0]["geometry"]["coordinates"][0]
origin = EXPECTED_ORIGIN
local = []
import math
for lon, lat, *_ in ring:
    x = (lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274))
    y = (lat - 40.4274) * 111040.0
    local.append((x - origin[0], y - origin[1]))
gis_bbox = [[min(p[0] for p in local), max(p[0] for p in local)],
            [min(p[1] for p in local), max(p[1] for p in local)]]

probe_payload = {asset}
bpy.data.libraries.write(str(PROBE), probe_payload, path_remap="RELATIVE_ALL", fake_user=True)
before_count = len(asset.all_objects)
source_hash = hashlib.sha256(ASSET.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(PROBE))
probe_asset = bpy.data.collections.get(COLLECTION_NAME)
assert probe_asset is not None
probe_names = [o.name for o in probe_asset.all_objects]
assert len(probe_names) == before_count
assert "BRNG_Rooftop_Room_Flat_Crown" in probe_names
assert not [o for o in probe_asset.all_objects if o.type in {"CAMERA", "LIGHT"}]

report = {
    "asset_id": "beering_hall",
    "owner": "Rosen",
    "asset_sha256": source_hash,
    "blender_version": bpy.app.version_string,
    "scene_after_asset_reopen": SCENE_NAME,
    "collection_after_asset_reopen": COLLECTION_NAME,
    "collection_object_count_after_reopen": before_count,
    "evaluated_asset_bounds_local_m": all_bounds,
    "structural_wall_bounds_local_m": structural,
    "gis_feature_251_local_bbox_m": gis_bbox,
    "manifest_origin_xy_m": EXPECTED_ORIGIN,
    "manifest_origin_preserved": True,
    "legacy_lower_roof_cluster_remaining": False,
    "new_roof_room_object_count": len(roof),
    "new_roof_room_names": roof_names,
    "unpacked_external_images": external_images,
    "linked_libraries": linked_libraries,
    "asset_cameras_lights": [],
    "collection_only_export_probe": str(PROBE.relative_to(ROOT)).replace("\\", "/"),
    "collection_probe_reopens": True,
    "collection_probe_object_count": len(probe_names),
    "collection_probe_has_rooftop_room": "BRNG_Rooftop_Room_Flat_Crown" in probe_names,
    "limitations": [
        "Structural shell and manifest placement were retained; source examiner had found bounding extents within approximately 0.29 m, but the complete wall-by-wall ring registration has not been independently recomputed here.",
        "GIS footprint does not verify rooftop room geometry or vertical height.",
        "GIS story-count attribute is nine; exact floor configuration and roof datum remain unverified.",
    ],
}
REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: report[k] for k in ["blender_version", "collection_object_count_after_reopen",
                                         "evaluated_asset_bounds_local_m", "structural_wall_bounds_local_m",
                                         "gis_feature_251_local_bbox_m", "new_roof_room_object_count",
                                         "collection_probe_reopens", "collection_probe_object_count",
                                         "asset_sha256"]}, indent=2))
