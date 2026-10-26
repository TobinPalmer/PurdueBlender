"""Reopen the Benjamin Harrison Hall asset, validate its source shell, and export the library."""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ASSET = ROOT / "modular" / "buildings" / "benjamin_harrison_hall.blend"
MANIFEST = ROOT / "modular" / "manifest.json"
GIS = HERE / "sources" / "benjamin_harrison_hall_gis_feature_85_raw.json"
BUILDING_ID = "benjamin_harrison_hall"
COLLECTION_NAME = "Asset_benjamin_harrison_hall"
PREVIEW_NAME = "PreviewOnly_benjamin_harrison_hall"
ORIGIN_LAT, ORIGIN_LON = 40.4274, -86.9137
ORIGIN_XY = (-1110.0, -260.0)
X_SCALE = 111412.84 * math.cos(math.radians(ORIGIN_LAT))
Y_SCALE = 111040.0


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
entry = next(a for a in manifest["assets"] if a.get("id") == BUILDING_ID)
assert entry["file"].replace("\\", "/") == f"buildings/{BUILDING_ID}.blend"
assert entry["collection"] == COLLECTION_NAME
assert entry["scene"] == "Building_benjamin_harrison_hall"
assert list(entry["placement_origin_xy_m"]) == list(ORIGIN_XY)

scene = bpy.context.scene
assert scene.name == entry["scene"]
collection = bpy.data.collections.get(COLLECTION_NAME)
preview = bpy.data.collections.get(PREVIEW_NAME)
assert collection is not None and preview is not None
export_objects = list(collection.objects)
preview_objects = list(preview.objects)
assert not [o.name for o in export_objects if o.type in {"CAMERA", "LIGHT"}]
assert len([o for o in preview_objects if o.type == "CAMERA"]) == 3
assert len([o for o in preview_objects if o.type == "LIGHT"]) == 1
preview_gear_names = {o.name for o in preview_objects if o.type in {"CAMERA", "LIGHT"}}

payload = json.loads(GIS.read_text(encoding="utf-8"))
feature = next(f for f in payload["features"] if int(f["attributes"]["FID"]) == 85)
assert feature["attributes"]["BLDG_ABBR"] == "HARR"
assert feature["attributes"]["BUILDING_N"] == "Benjamin Harrison Residence Hall"
lonlat_ring = feature["geometry"]["rings"][0][:-1]
source_ring = [((lon - ORIGIN_LON) * X_SCALE - ORIGIN_XY[0],
                (lat - ORIGIN_LAT) * Y_SCALE - ORIGIN_XY[1]) for lon, lat, *_ in lonlat_ring]

base = collection.objects.get("HARR_Ground_Plinth_Base")
assert base is not None
depsgraph = bpy.context.evaluated_depsgraph_get()
evaluated = base.evaluated_get(depsgraph)
mesh = evaluated.to_mesh()
try:
    verts = [evaluated.matrix_world @ v.co for v in mesh.vertices]
    min_z = min(v.z for v in verts)
    model_ring = sorted(set((round(v.x, 6), round(v.y, 6)) for v in verts if abs(v.z - min_z) < 1e-4))
finally:
    evaluated.to_mesh_clear()
assert len(model_ring) == len(source_ring) == 28

def directed_error(a, b):
    return max(min(math.dist(p, q) for q in b) for p in a)

footprint_error = max(directed_error(model_ring, source_ring), directed_error(source_ring, model_ring))
assert footprint_error < 0.02, f"GIS/model shell mismatch {footprint_error:.5f} m"

def evaluated_bounds(objs):
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for obj in objs:
        if obj.type == "MESH":
            ev = obj.evaluated_get(dg)
            me = ev.to_mesh()
            try:
                pts.extend(ev.matrix_world @ v.co for v in me.vertices)
            finally:
                ev.to_mesh_clear()
        elif obj.type in {"CURVE", "FONT", "SURFACE", "META"}:
            pts.extend(obj.matrix_world @ Vector(c) for c in obj.bound_box)
    return [[float(min(p[i] for p in pts)), float(max(p[i] for p in pts))] for i in range(3)]

before = {
    "asset_path": str(ASSET),
    "asset_sha256": sha256(ASSET),
    "blender_version": bpy.app.version_string,
    "manifest_id_path_collection_scene_match": True,
    "manifest_placement_origin_xy_m": list(ORIGIN_XY),
    "export_collection": COLLECTION_NAME,
    "export_object_count": len(export_objects),
    "export_object_names": sorted(o.name for o in export_objects),
    "export_object_types": {},
    "preview_collection": PREVIEW_NAME,
    "preview_camera_names": sorted(o.name for o in preview_objects if o.type == "CAMERA"),
    "preview_light_names": sorted(o.name for o in preview_objects if o.type == "LIGHT"),
    "camera_or_light_in_export": False,
    "gis_feature_id": int(feature["attributes"]["FID"]),
    "gis_name": feature["attributes"]["BUILDING_N"],
    "gis_distinct_vertices": len(source_ring),
    "model_distinct_base_vertices": len(model_ring),
    "gis_model_max_symmetric_nearest_vertex_error_m": footprint_error,
    "model_shell_base_z_local_m": min_z,
    "evaluated_collection_bounds_local_m": evaluated_bounds(export_objects),
    "manifest_object_count_before_shared_refresh": entry.get("object_count", len(entry.get("objects", []))),
    "manifest_object_names_before_shared_refresh": len(entry.get("objects", [])),
    "removed_from_asset_collection": sorted(set(entry.get("objects", [])) - {o.name for o in export_objects}),
    "external_file_images": [img.filepath for img in bpy.data.images if img.source == "FILE" and not img.packed_file],
    "linked_libraries": [str(lib.filepath) for lib in bpy.data.libraries if lib.filepath]
}
for obj in export_objects:
    before["export_object_types"][obj.type] = before["export_object_types"].get(obj.type, 0) + 1
assert set(before["removed_from_asset_collection"]) in (set(), preview_gear_names)
assert not set(before["export_object_names"]) - set(entry.get("objects", [])), "Export contains names absent from manifest"
assert not before["external_file_images"]
assert not before["linked_libraries"]

probe_path = HERE / "collection_export_probe.blend"
bpy.data.libraries.write(str(probe_path), {collection}, path_remap="RELATIVE_ALL", fake_user=True)
bpy.ops.wm.open_mainfile(filepath=str(probe_path))
exported = bpy.data.collections.get(COLLECTION_NAME)
assert exported is not None
probe_objects = list(exported.objects)
assert not [o.name for o in probe_objects if o.type in {"CAMERA", "LIGHT"}]
assert len(probe_objects) == before["export_object_count"]
assert {o.name for o in probe_objects} == set(before["export_object_names"])
after_external_images = [img.filepath for img in bpy.data.images if img.source == "FILE" and not img.packed_file]
after_libraries = [str(lib.filepath) for lib in bpy.data.libraries if lib.filepath]
assert not after_external_images and not after_libraries

result = {
    "verified_at_utc": datetime.now(timezone.utc).isoformat(),
    **before,
    "collection_only_export_probe": str(probe_path.relative_to(ROOT)),
    "reopened_export_object_count": len(probe_objects),
    "reopened_export_object_types": {t: sum(o.type == t for o in probe_objects) for t in sorted({o.type for o in probe_objects})},
    "reopened_export_has_camera_or_light": False,
    "reopened_export_object_names_match_source_collection": True,
    "reopened_export_external_file_images": after_external_images,
    "reopened_export_external_libraries": after_libraries,
    "manifest_note": ("Shared manifest still includes preview gear; coordinator should refresh the object list/count." if before["removed_from_asset_collection"] else "Shared manifest object list/count already matches the repaired export.")
}
(HERE / "reopen_verification.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({k: result[k] for k in ["blender_version", "export_collection", "export_object_count", "export_object_types", "camera_or_light_in_export", "preview_camera_names", "preview_light_names", "gis_model_max_symmetric_nearest_vertex_error_m", "evaluated_collection_bounds_local_m", "reopened_export_object_count", "reopened_export_has_camera_or_light", "removed_from_asset_collection"]}, indent=2), flush=True)
