import json
from pathlib import Path

import bpy

ASSET_ID = "massing_the_church_of_jesus_christ_of_latter_day_saints_6f2a451"
EXPECTED_SCENE = "Building_" + ASSET_ID
EXPECTED_COLLECTION = "Asset_" + ASSET_ID
EXPECTED_OBJECT = "The Church of Jesus Christ of Latter-day Saints"
ROOT = Path(__file__).resolve().parents[2]
BLEND = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
OUT = Path(__file__).resolve().parent / "reopen_validation.json"

scene = bpy.context.scene
collection = bpy.data.collections.get(EXPECTED_COLLECTION)
obj = bpy.data.objects.get(EXPECTED_OBJECT)
errors = []
if scene.name != EXPECTED_SCENE:
    errors.append(f"Scene name mismatch: {scene.name!r}")
if collection is None:
    errors.append("Manifest collection missing")
if obj is None:
    errors.append("Manifest object missing")
if collection and (len(collection.objects) != 1 or obj not in collection.objects[:]):
    errors.append("Export collection does not contain exactly the manifest object")
if obj and obj.type != "MESH":
    errors.append(f"Expected one mesh object, got {obj.type}")
if obj and obj.get("stable_building_id") != ASSET_ID:
    errors.append("Stable ID custom property missing or mismatched")
if len(bpy.data.scenes) != 1:
    errors.append(f"Expected one scene, got {len(bpy.data.scenes)}")

verts = [tuple(v.co) for v in obj.data.vertices] if obj else []
bounds = None
if verts:
    bounds = {
        axis: [round(min(v[i] for v in verts), 4), round(max(v[i] for v in verts), 4)]
        for i, axis in enumerate("xyz")
    }
    if bounds["z"][1] < 5.0 or bounds["z"][1] > 8.0:
        errors.append(f"Unexpected estimated overall height: {bounds['z'][1]}")

result = {
    "asset_id": ASSET_ID,
    "blend_path": str(BLEND),
    "blender_version": bpy.app.version_string,
    "reopened_scene": scene.name,
    "reopened_collection": collection.name if collection else None,
    "reopened_collection_object_names": sorted(o.name for o in collection.objects) if collection else [],
    "reopened_scene_count": len(bpy.data.scenes),
    "reopened_object_type": obj.type if obj else None,
    "mesh_vertex_count": len(verts),
    "mesh_face_count": len(obj.data.polygons) if obj else None,
    "mesh_campus_bounds_m": bounds,
    "estimated_height_properties": {
        "overall_m": scene.get("estimated_height_m"),
        "status": scene.get("height_status"),
        "legacy_gis_extrution_units": scene.get("legacy_gis_extrution_units"),
    },
    "bounds_note": "Campus-world mesh coordinates. Minimum z below zero is the non-structural access ramp slope beyond the GIS shell footprint.",
    "checks_passed": not errors,
    "errors": errors,
}
OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
if errors:
    raise RuntimeError("; ".join(errors))
